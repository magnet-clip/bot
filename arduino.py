import serial
import threading
import re


class ArduinoSerial:
    def __init__(self, port, speed):
        self.conn = serial.Serial(port, speed, timeout=0)
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        self.interrupted = False

    def run(self):
        while not self.interrupted:
            char = self.conn.read()
            # todo we have to see what comes from arduino
            print("[{0}]".format(char))

    def shutdown(self):
        self.interrupted = True
        self.thread.join()
        self.conn.close()

    def send_command(self, angle1, angle2, devices):
        # todo pack into a command
        pass
