import helper
import dbman
from datetime import timedelta
import pygal
from wand.api import library
import wand.color
import wand.image


def make_answer_list(items):
    res = ""
    for id, name in items:
        res += " * {0}: /grant{1}, /delete{1}, /ban{1}\r\n".format(name, id)
    return res


class Handler:
    def __init__(self, bot, man, cam, db: dbman.DatabaseManager):
        self.bot = bot
        self.man = man
        self.cam = cam
        self.db = db

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
                    man.get_admin_id(),
                    "User {0} id [{1}] wants to get access; Type /grant{1} to allow, /ban{1} to ban him".format(
                        message.from_user.first_name, user_id)
                )

    def grant_access(self, message, grantee_id):
        print("Grant access command")
        bot = self.bot
        man = self.man

        if not self._authorize_admin(message.from_user.id, message.chat.id):
            return

        if not man.grant_access(grantee_id):
            bot.send_message(message.from_user.id, "Failed to grant access")
        else:
            bot.send_message(grantee_id, "Willkommen!")

    def delete_user(self, message, grantee_id):
        print("Delete user command")
        if not self._authorize_admin(message.from_user.id, message.chat.id):
            return

        if not self.man.delete_user(grantee_id):
            self.bot.send_message(message.from_user.id, "Failed to delete user")

    def ban_user(self, message, grantee_id):
        print("Ban user command")
        if not self._authorize_admin(message.from_user.id, message.chat.id):
            return

        if not self.man.ban_user(grantee_id):
            self.bot.send_message(message.from_user.id, "Failed to ban user")

    def list_users(self, message, kind):
        print("List users, kind: {0}!".format(kind))
        man = self.man
        if not self._authorize_admin(message.from_user.id, message.chat.id):
            return

        answer = ""
        if kind == "b":
            answer = make_answer_list(man.list_banned())
        elif kind == "g":
            answer = make_answer_list(man.list_granted())
        elif kind == "p":
            answer = make_answer_list(man.list_pending())
        else:
            answer = """
            Choose one:
                * /listg - granted
                * /listp - pending
                * /listb - banned
            """
        if len(answer) == 0:
            answer = "No users!"
        self.bot.send_message(message.chat.id, answer)


    def answer(self, message, text):
        bot.send_message(message.chat.id, text)

    def make_and_send_plot(self, message, field):
        file_name = './test.svg'
        png_filename = './test.png'
        bot = self.bot
        items = self.db.fetch_last(timedelta(seconds=5), field)
        print(items)

        ## -- creating chart
        try:
            chart = pygal.Line()
            labels = list([str(item['time'].strftime('%H:%M:%S')) for item in items])
            print(labels)
            chart.x_labels = labels

            values = list([float(item['value']) for item in items])
            print(values)

            chart.add(field, values)
            chart.render_to_file(file_name)
        except Exception as e:
            print(e)


        ## -- converting to png from svg
        try:
            with open(file_name, 'rb') as svg_file:
                with wand.image.Image(blob=svg_file.read(), format='svg') as img:
                    with wand.color.Color('transparent') as bg_color:
                        library.MagickSetBackgroundColor(img.wand, bg_color.resource)
                    png_image = img.make_blob('png32')

                    with open(png_filename, 'wb') as out:
                        out.write(png_image)

        except Exception as e:
            print(e)


        ## -- sending to user
        try:
            temp_file = open(png_filename, 'rb')
            try:
                print("Sending...")
                bot.send_photo(message.chat.id, temp_file)
            except Exception as e:
                bot.send_message(message.chat.id, "Failed to send a photo :(")
                print("Failed to send photo: {0}".format(e))
            finally:
                temp_file.close()
        except Exception as e:
            bot.send_message(message.chat.id, "Failed to send a photo :(")

    def make_snapshot(self, message):
        bot = self.bot
        cam = self.cam
        print("User %s id [%s] requested a photo" % (message.from_user.first_name, message.from_user.id))

        if not self._authorize_user(message.from_user.id):
            bot.send_message(message.chat.id, "You have to be authorized to request photo")
            return

        file_name = cam.make_and_save_snapshot()
        try:
            temp_file = open(file_name, 'rb')
            try:
                print("Sending...")
                bot.send_photo(message.chat.id, temp_file)
            except Exception as e:
                bot.send_message(message.chat.id, "Failed to send a photo :(")
                print("Failed to send photo: {0}".format(e))
            finally:
                temp_file.close()
        except Exception as e:
            bot.send_message(message.chat.id, "Failed to send a photo :(")

        try:
            helper.clear_folder("./snaps")
        except Exception as e:
            print("Failed to delete temp files: {0}".format(e))
