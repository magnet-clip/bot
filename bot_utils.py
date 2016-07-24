import time
import random
import os
import shutil
import configparser
import picamera
import re

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

def fetch_id(text, command):
    regex = "^/{0} +(\d+)$".format(command)
    print("... regex is %s" % regex)
    pattern = re.compile(regex)
    matches = re.findall(pattern, text)
    print(matches)

    if len(matches) == 0:
        return None
    else:
        return matches[0]

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
        uid = str(user_id)
        if self.is_super_user(uid):
            return True

        if uid in self._config:
            return self._config[uid]["status"] == "granted"

        return False

    def has_super_user(self):
        print("Current superuser id is %s" % self._config["superuser"]["id"])
        return self._config["superuser"]["id"] != 'NONE'

    def is_super_user(self, user_id):
        uid = str(user_id)
        return self._config["superuser"]["id"] == uid

    def set_super_user(self, user_id):
        uid = str(user_id)
        if not self.has_super_user():
            print(" -> no superuser yet defined")
            self._config["superuser"]["id"] = uid
            self.save()
            return self.DONE
        elif self.is_super_user(uid):
            print(" -> he is already")
            return self.OK
        else:
            return self.FAIL

    def get_admin_id(self):
        return self._config["superuser"]["id"]

    def is_user_pending(self, user_id):
        uid = str(user_id)
        if user_id in self._config:
            return self._config[uid]["status"] == "pending"
        else:
            return False

    def is_user_banned(self, user_id):
        uid = str(user_id)
        if uid in self._config:
            return self._config[uid]["status"] == "banned"
        else:
            return False

    def register_user_pending(self, user_id):
        uid = str(user_id)
        if user_id in self._config:
            return self.FAIL
        self._config.add_section(uid)
        self._config[uid]["status"] = "pending"
        self.save()
        return self.OK

    def grant_access(self, user_id):
        uid = str(user_id)
        if not (user_id in self._config):
            self._config.add_section(uid)
        self._config[uid]["status"] = "granted"
        self.save()

    def ban_user(self, user_id):
        uid = str(user_id)
        if not (user_id in self._config):
            self._config.add_section(uid)
        self._config[uid]["status"] = "banned"
        self.save()

    def delete_user(self, user_id):
        uid = str(user_id)
        if user_id in self._config:
            self._config.remove_section(uid)
        self.save()
