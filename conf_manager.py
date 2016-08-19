from os import path
from configparser import ConfigParser
import measures

class ConfManager:
    _CONFIG_FILE = "bot.config"
    DONE = "DONE"
    FAIL = "FAIL"
    NONE = "NONE"
    OK = "OK"

    def _ensure_superuser_section(self):
        if not self._config.has_section("superuser"):
            self._config.add_section("superuser")
            self._config["superuser"]["id"] = self.NONE
            self.save()

    def __init__(self, config_file_name=""):
        if config_file_name != "":
            self._CONFIG_FILE = config_file_name

        if not path.isfile("./" + self._CONFIG_FILE):
            open("./" + self._CONFIG_FILE, "w").close()

        self._config = ConfigParser()
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
        self._config["superuser"]["id"] = self.NONE
        self.save()

    def has_super_user(self):
        self._ensure_superuser_section()
        print("Current superuser id is %s" % self._config["superuser"]["id"])
        return self._config["superuser"]["id"] != self.NONE

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

    def user_exists(self, user_id):
        return self._config.has_section(user_id)

    def _check_by_criteria(self, user_id, value):
        uid = str(user_id)
        if user_id in self._config:
            return self._config[uid]["status"] == value
        else:
            return False

    def is_user_granted(self, user_id):
        return self._check_by_criteria(user_id, "granted")

    def is_user_pending(self, user_id):
        return self._check_by_criteria(user_id, "pending")

    def is_user_banned(self, user_id):
        return self._check_by_criteria(user_id, "banned")

    def register_user_pending(self, user_id, user_name=""):
        uid = str(user_id)
        if user_id in self._config:
            return

        self._config.add_section(uid)
        self._config[uid]["status"] = "pending"
        self._config[uid]["name"] = user_name
        self.save()

    def grant_access(self, user_id):
        uid = str(user_id)
        if not (uid in self._config):
            return False
        self._config[uid]["status"] = "granted"
        self.save()
        return True

    def ban_user(self, user_id):
        uid = str(user_id)
        if not (uid in self._config):
            return False
        self._config[uid]["status"] = "banned"
        self.save()
        return True

    def delete_user(self, user_id):
        uid = str(user_id)
        if uid in self._config:
            self._config.remove_section(uid)
            self.save()
            return True
        return False

    def _list_by_criteria(self, criteria):
        res = []
        for name in self._config.sections():
            print(" --> %s" % name)
            if name != 'superuser' and criteria(name):
                if 'name' in self._config[name]:
                    res.append((name, self._config[name]['name']))
                else:
                    res.append((name, ""))
        return res

    def list_banned(self):
        return self._list_by_criteria(self.is_user_banned)

    def list_granted(self):
        return self._list_by_criteria(self.is_user_granted)

    def list_pending(self):
        return self._list_by_criteria(self.is_user_pending)

    # def add_notification(self, uuid, name, op, value):
    #     if not self.is_user_allowed(uuid):
    #         return False
    #
    #     op = vars.parse_op(op)
    #     if not op:
    #         return False
    #
    #     var_name = vars.find_var_by_name(name)
    #     if not var_name:
    #         return False
    #
    #     record_name = "{0} {1}"
    #     self._config[uuid][]
    #
    # def mute_notification(self, uuid, name):
    #     pass
    #
    # def unmute_notification(self, uuid):
    #     pass
    #
    # def remove_notification(self, uuid, name):
    #     pass
    #
    # def find_users_to_notify(self, var_name, value):
    #     res = []
    #     for uuid in self._config.sections():
    #         if uuid == 'superuser':
    #             continue
    #
    #         section = self._config[uuid]
    #         # TODO CHECK CONSTRAINTS
    #         # TODO NO FORMAT EXISTS => FIRST CREATE A METHOD TO ACCEPT CONSTRAINTS FROM USER
    #         # TODO OR DAMN IT AND EDIT CONSTRAINTS MANUALLY? BAD IDEA, PEOPLE WILL GET TIRED
    #         # COMMANDS: /notify temperature > 35
    #         #           /notify temperature < 10
    #         #           /notify motion
    #         #           /notify gas > 400
    #         #           /notify light > 100
    #         #           /mute gas
    #         #           /unmute gas
    #         # TODO STORE WHEN LAST NOTIFIED AND DO NOT SEND TOO MUCH NOTIFICATIONS
    #
    #
    #     return res
