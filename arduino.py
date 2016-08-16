import serial
import threading
import queue
from dbman import DatabaseManager
import re
from datetime import datetime


class SerialHandler(threading.Thread):
    def __init__(self, cnn: serial.Serial, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.conn = cnn
        self.interrupted = False
        self.queue = queue.Queue()
        self.last_minutes = -1
        # TODO read last minutes from database (not really important feature)

    def interrupt(self):
        self.interrupted = True

    def read(self):
        try:
            message = self.conn.readline()
        except Exception as e:
            message = b''
            print(e)

        if message != b'':
            decoded = message.decode('utf-8')
            decoded = re.sub("[\r\n]", "", decoded)
            items = decoded.split(';')

            if len(items) < 7:
                continue

            minutes = datetime.now().minute
            if minutes != self.last_minutes:
                self.last_minutes = minutes

                self.db.add({
                    'co2': items[0],
                    'gas': items[1],
                    'light': items[2],
                    'motion': items[3],
                    'cameraAllowed': items[4],
                    'humidity': items[5],
                    'temperature': items[6]
                })

            # TODO Somehow check if one of the values hits limits
            # TODO and notify user if necessary

            # TODO Start with motion sensor, it is either YES or NO

            # TODO In order to do it I have to have access to configuration
            # TODO and to message sending facility

            # TODO Configuration can be injected

            # TODO What about message sending? It works in a loop, 
            # TODO so I can use a queue for this! Hence I will have to inject a Queue
            # TODO and check it in main loop!

        if not self.queue.empty():
            item = self.queue.get()
            print("Got message [%s]!" % item)


    def run(self):
        try:
            while not self.interrupted:
                self.read()
        finally:
            self.conn.close()

    def send_message(self, item):
        self.queue.put(item)
