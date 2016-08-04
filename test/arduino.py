import unittest
import arduino


class TestArduino(unittest.TestCase):
    def test_just_run(self):
        aino = arduino.ArduinoSerial('COM5', 9600)
        aino.shutdown()
