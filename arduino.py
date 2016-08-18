import vars
import serial
import threading
from dbman import DatabaseManager
import re
from datetime import datetime


class SerialHandler(threading.Thread):
    def __init__(self, cnn: serial.Serial, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.conn = cnn
        self.interrupted = False
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
                vars.CO2: co2,
                vars.GAS: gas,
                vars.LIGHT: light,
                vars.MOTION: motion,
                vars.CANCAM: canCam,
                vars.HUMIDITY: hum,
                vars.TEMPERATURE: temp
            })

            self.inform_on(vars.CO2, co2)
            self.inform_on(vars.GAS, gas)
            self.inform_on(vars.LIGHT, light)
            self.inform_on(vars.MOTION, motion)
            self.inform_on(vars.HUMIDITY, hum)
            self.inform_on(vars.TEMPERATURE, temp)

    def inform_on(self, param, its_value):
        pass

