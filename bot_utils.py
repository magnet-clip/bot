import os
import configparser
import re

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
    
    def _ensure_superuser_section(self):
        if not self._config.has_section("superuser"):
            self._config.add_section("superuser")
            self._config["superuser"]["id"] = 'NONE'
            self.save()

    def __init__(self, config_file_name=""):
        if config_file_name != "":
            self._CONFIG_FILE = config_file_name
        
        if not os.path.isfile("./" + self._CONFIG_FILE):
            open("./" + self._CONFIG_FILE).close()
        
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
        
    def dispose_super_user(self):
        self._ensure_superuser_section()
        self._config["superuser"]["id"] = 'NONE'
        self._save()

    def has_super_user(self):
        print("Current superuser id is %s" % self._config["superuser"]["id"])
        self._ensure_superuser_section()
        return self._config["superuser"]["id"] != 'NONE'

    def is_super_user(self, user_id):
        uid = str(user_id)
        self._ensure_superuser_section()
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
