import serial
import threading
import queue


class SerialHandler(threading.Thread):
    def __init__(self, cnn: serial.Serial):
        super().__init__()
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
                    # todo save into database
                    for item in items:
                        print(item)
                    print("--------------")
                if not self.queue.empty():
                    # todo send message to ino
                    item = self.queue.get()
                    print("Got message [%s]!" % item)
        finally:
            self.conn.close()

    def send_message(self, item):
        self.queue.put(item)