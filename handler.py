import bot_helper


class Handler:
    def __init__(self, bot, man, cam):
        self.bot = bot
        self.man = man
        self.cam = cam

    def _authorize_admin(self, user_id, chat_id):
        bot = self.bot
        man = self.man

        if not man.is_super_user(user_id):
            bot.send_message(chat_id, "You are not authorized to run this command")
            return False

        return True

    def _authorize_user(self, user_id):
        bot = self.bot
        man = self.man
        if not man.is_user_allowed(user_id):
            bot.send_message(user_id, "No access! Type /getaccess if you want to request access")
            return False

        return True

    def _fetch_user_id(self, text, chat_id):
        bot = self.bot

        grantee_id = bot_helper.fetch_id(text, 'grant')
        if grantee_id == None:
            bot.send_message(chat_id, "Failed to fetch user id")

        return grantee_id

    def set_boss(self, message):
        bot = self.bot
        man = self.man
        print("User %s id [%s] wants to be a boss" % (message.from_user.first_name, message.from_user.id))
        user_id = message.from_user.id
        res = man.set_super_user(user_id)
        print("... and the answer is %s" % res)
        if res == man.DONE:
            bot.send_message(message.chat.id, "You are the king now")
        elif res == man.OK:
            bot.send_message(message.chat.id, "I know")
        else:
            bot.send_message(message.chat.id, "Nope")

    def resign(self, message):
        bot = self.bot
        man = self.man
        print("User %s id [%s] wants to be resign" % (message.from_user.first_name, message.from_user.id))
        user_id = message.from_user.id

        if man.is_super_user(user_id):
            man.dispose_super_user()
            bot.send_message(message.chat.id, "We have a vacancy now")

    def get_access(self, message):
        bot = self.bot
        man = self.man
        print("User %s id [%s] is requesting access" % (message.from_user.first_name, message.from_user.id))
        user_id = message.from_user.id
        if man.is_user_allowed(user_id):
            bot.send_message(user_id, "You have an access ALREADY")
        elif man.is_user_pending(user_id):
            bot.send_message(user_id, "Still under review!")
        elif man.is_user_banned(user_id):
            bot.send_message(user_id, "No and don't ask again!")
        else:
            print("User %s id [%s] wants to get access" % (message.from_user.first_name, user_id))
            bot.send_message(user_id, "Your application is under review")
            man.register_user_pending(user_id, message.from_user.username)

            if man.has_super_user():
                bot.send_message(
                    man.get_admin_id(), \
                    "User {0} id [{1}] wants to get access; Type /grant {1} to allow, /ban {1} to ban him".format(
                        message.from_user.first_name, user_id) \
                    )

    def grant_access(self, message):
        print("Grant access command")
        bot = self.bot
        man = self.man

        if not self._authorize_admin(message.from_user.id, message.chat.id): return
        grantee_id = self._fetch_user_id(message.text, message.chat.id)
        if grantee_id == None: return

        man.grant_access(grantee_id)
        bot.send_message(grantee_id, "Willkommen!")

    def delete_user(self, message):
        print("Delete user command")
        man = self.man

        if not self._authorize_admin(message.from_user.id, message.chat.id): return
        grantee_id = self._fetch_user_id(message.text, message.chat.id)
        if grantee_id == None: return

        man.delete_user(grantee_id)

    def ban_user(self, message):
        print("Ban user command")
        man = self.man

        if not self._authorize_admin(message.from_user.id, message.chat.id): return
        grantee_id = self._fetch_user_id(message.text, message.chat.id)
        if grantee_id == None: return

        man.ban_user(grantee_id)

    def make_snapshot(self, message):
        bot = self.bot
        cam = self.cam
        print("User %s id [%s] requested a photo" % (message.from_user.first_name, message.from_user.id))

        if not self._authorize_user(message.from_user.id):
            return

        file_name = cam.make_and_save_snapshot()
        temp_file = open(file_name, 'rb')
        try:
            print("Sending...")
            bot.send_photo(message.chat.id, temp_file)
        except Exception as e:
            print("Failed to send photo: {0}".format(e))
        finally:
            temp_file.close()

        try:
            bot_helper.clear_folder("./snaps")
        except Exception as e:
            print("Failed to delete temp files: {0}".format(e))
