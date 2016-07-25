import picamera
import time
import random


class Camera():
    def _get_temp_file_name(self):
        return str(random.randint(10000, 99999)) + "_" + str(int(round(time.time() * 1000)))

    def make_and_save_snapshot(self):
        file_name = "./snaps/" + self._get_temp_file_name() + ".jpg"
        print("File is %s" % file_name)
        temp_file = open(file_name, 'wb')
        with picamera.PiCamera() as camera:
            camera.resolution = (640, 480)
            #camera.start_preview()
            time.sleep(2)
            camera.capture(temp_file)
            temp_file.close()
        return file_name