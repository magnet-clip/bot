import time
import random
import os
import shutil
import configparser
import picamera


def get_temp_file_name():
    return str(random.randint(10000, 99999)) + "_" + str(int(round(time.time() * 1000)))

def make_and_save_snapshot():
    file_name = "./snaps/" + get_temp_file_name() + ".jpg"
    print("File is %s" % file_name)
    temp_file = open(file_name, 'wb')
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        #camera.start_preview()
        time.sleep(2)
        camera.capture(temp_file)
        temp_file.close()
    return file_name


def clear_folder(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


class Config:
    _CONFIG_FILE = "bot.config"
    DONE = "DONE"
    FAIL = "FAIL"
    OK = "OK"

    def __init__(self):
        self._config = configparser.ConfigParser()
        self._config.read("./" + self._CONFIG_FILE)

    def save(self):
        with open("./" + self._CONFIG_FILE, 'w') as cnf:
            self._config.write(cnf)

    def is_user_allowed(self, user_id):
        return self.is_super_user(user_id) or user_id in self._config

    def has_super_user(self):
        print("Current superuser id is %s" % self._config["superuser"]["id"])
        return self._config["superuser"]["id"] != 'NONE'

    def is_super_user(self, user_id):
        return self._config["superuser"]["id"] == str(user_id)

    def set_super_user(self, user_id):
        if not self.has_super_user():
            print(" -> no superuser yet defined")
            self._config["superuser"]["id"] = str(user_id)
            self.save()
            return self.DONE
        elif self.is_super_user(str(user_id)):
            print(" -> he is already")
            return self.OK
        else:
            return self.FAIL

    def get_admin_id(self):
        return self._config["superuser"]["id"]

man = Config()
