import serial
import threading
import re


class ArduinoSerial:
    def __init__(self, port, speed):
        self.conn = serial.Serial(port, speed, timeout=0)
        print("Opening serial connection")
        # self.thread = threading.Thread(target=self.run)
        # self.thread.start()
        self.interrupted = False

    def run(self):
        while not self.interrupted:
            line = self.conn.readline()
            if line != b'':
                print(line)
                pass
        print("Interrupted!")

    def shutdown(self):
        self.interrupted = True
        # self.thread.join()
        self.conn.close()
        print("Closed serial connection")

    def send_command(self, angle1, angle2, devices):
        # todo pack into a command
        pass
