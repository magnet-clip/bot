import serial
import re

class ArduinoSerial:
    def __init__(self, port, speed):
        self.conn = serial.Serial(port, speed)
