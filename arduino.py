import serial
import threading
import queue
from dbman import DatabaseManager


class SerialHandler(threading.Thread):
    def __init__(self, cnn: serial.Serial, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.conn = cnn
        self.interrupted = False
        self.queue = queue.Queue()

    def interrupt(self):
        self.interrupted = True

    def run(self):
        try:
            while not self.interrupted:
                message = self.conn.readline()
                if message != b'':
                    decoded = message.decode('utf-8')
                    items = decoded.split(';')

                    if len(items) < 7:
                        continue

                    self.db.add({
                        'co2': items[0],
                        'gas': items[1],
                        'light': items[2],
                        'motion': items[3],
                        'cameraAllowed': items[4],
                        'humidity': items[5],
                        'temperature': items[6]
                    })

                if not self.queue.empty():
                    item = self.queue.get()
                    print("Got message [%s]!" % item)
        finally:
            self.conn.close()

    def send_message(self, item):
        self.queue.put(item)