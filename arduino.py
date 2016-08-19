from measures import Measures
import serial
import threading
from db_manager import DatabaseManager
import re
from datetime import datetime
from bot_manager import BotManager as EventsHandler


class SerialHandler(threading.Thread):
    def __init__(self, cnn: serial.Serial, db: DatabaseManager, handler: EventsHandler):
        super().__init__()
        self.db = db
        self.conn = cnn
        self.interrupted = False
        self.handler = handler
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

            if len(items) == 7:
                self.handle_items(items)

        # if not self.queue.empty():
        #     item = self.queue.get()
        #     print("Got message [%s]!" % item)

    def run(self):
        try:
            while not self.interrupted:
                self.read()
        finally:
            self.conn.close()

    # def send_message(self, item):
    #     self.queue.put(item)

    def handle_items(self, items):
        minutes = datetime.now().minute
        if minutes != self.last_minutes:
            self.last_minutes = minutes

            co2 = int(items[0])
            gas = int(items[1])
            light = int(items[2])
            motion = int(items[3])
            canCam = int(items[4])
            hum = float(items[5])
            temp = float(items[6])

            self.db.add({
                Measures.CO2: co2,
                Measures.GAS: gas,
                Measures.LIGHT: light,
                Measures.MOTION: motion,
                Measures.CANCAM: canCam,
                Measures.HUMIDITY: hum,
                Measures.TEMPERATURE: temp
            })

            # self.handler.inform(vars.CO2, co2)
            # self.handler.inform(vars.GAS, gas)
            # self.handler.inform(vars.LIGHT, light)
            # self.handler.inform(vars.MOTION, motion)
            # self.handler.inform(vars.HUMIDITY, hum)
            # self.handler.inform(vars.TEMPERATURE, temp)
