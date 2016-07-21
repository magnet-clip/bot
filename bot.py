import config
import telebot
import bot_utils
import time
import logging
import sys
import signal

def ctrlchandler(signum, frame):
    print("Bye!")
    sys.exit()

signal.signal(signal.SIGINT, ctrlchandler)

logger = telebot.logger
telebot.logger.setLevel(logging.WARN)

bot = telebot.TeleBot(config.token, threaded=False)

#@bot.inline_handler(lambda query: len(query.query) > 0)
#def inline_handler(query):
#	res = telebot.types.InlineQueryResultArticle( '1','Answer', telebot.types.InputTextMessageContent(query.query))
#	bot.answer_inline_query(query.id, [res])

@bot.message_handler(commands=['boss'])
def set_boss(message):
    print("User %s id [%s] wants to be a boss" % (message.from_user.first_name, message.from_user.id))
    user_id = message.from_user.id
    res = bot_utils.man.set_super_user(user_id)
    print("... and the answer is %s" % res)
    if res == bot_utils.man.DONE:
        bot.send_message(message.chat.id, "You are the king now")
    elif res == bot_utils.man.OK:
        bot.send_message(message.chat.id, "I know")
    else:
        bot.send_message(message.chat.id, "Nope")

@bot.message_handler(commands=['getaccess'])
def get_access(message):
    print("User %s id [%s] is requesting access" % (message.from_user.first_name, message.from_user.id))
    user_id = message.from_user.id
    if bot_utils.man.is_user_allowed(user_id):
        bot.send_message(user_id, "You have an access ALREADY")
    elif bot_utils.man.is_user_pending(user_id):
        bot.send_message(user_id, "Still under review!")
    elif bot_utils.man.is_user_banned(user_id):
        bot.send_message(user_id, "No and don't ask again!")
    else:
        print("User %s id [%s] wants to get access" % (message.from_user.first_name, user_id))
        bot.send_message(
            bot_utils.man.get_admin_id(),  \
            "User {0} id [{1}] wants to get access; Type /grant {1} to allow, /ban {1} to ban him".format(message.from_user.first_name, user_id) \
        )
        bot.send_message(user_id, "Your application is under review")
        bot_utils.register_user_pending(user_id)

@bot.message_handler(commands=['grant'])
def grant_access(message):
    print("Grant access command")

    user_id = message.from_user.id
    grantee_id = bot_utils.fetch_id(message.text, 'grant')

    if not bot_utils.man.is_super_user(user_id):
        bot.send_message(message.chat.id, "You are not authorized to run this command")
        return

    if grantee_id == None:
        bot.send_message(message.chat.id, "Failed to fetch user id")
        return

    bot_utils.man.grant_access(grantee_id)
    bot.send_message(grantee_id, "Willkommen!")


@bot.message_handler(commands=['delete'])
def delete_user(message):
    print("Delete user command")

    user_id = message.from_user.id
    grantee_id = bot_utils.fetch_id(message.text, 'delete')

    if not bot_utils.man.is_super_user(user_id):
        bot.send_message(message.chat.id, "You are not authorized to run this command")
        return

    if grantee_id == None:
        bot.send_message(message.chat.id, "Failed to fetch user id")
        return

    bot_utils.man.delete_user(grantee_id)

@bot.message_handler(commands=['ban'])
def ban_user(message):
    print("Ban user command")

    user_id = message.from_user.id
    grantee_id = bot_utils.fetch_id(message.text, 'ban')

    if not bot_utils.man.is_super_user(user_id):
        bot.send_message(message.chat.id, "You are not authorized to run this command")
        return

    if grantee_id == None:
        bot.send_message(message.chat.id, "Failed to fetch user id")
        return

    bot_utils.man.ban_user(grantee_id)

@bot.message_handler(commands=['photo'])
def make_snapshot(message):
    print("User %s id [%s] requested a photo" % (message.from_user.first_name, message.from_user.id))

    if not bot_utils.man.is_user_allowed(message.from_user.id):
        bot.send_message(message.chat.id, "No access! Type /getaccess if you want to request access")
        return

    file_name = bot_utils.make_and_save_snapshot()
    temp_file = open(file_name, 'rb')
    try:
        print("Sending...")
        bot.send_photo(message.chat.id, temp_file)
    except Exception as e:
        print("Failed to send photo: {0}".format(e))
    finally:
        temp_file.close()

    try:
        bot_utils.clear_folder("./snaps")
    except Exception as e:
        print("Failed to delete temp files: {0}".format(e))

#@bot.message_handler(content_types=["text"])
#def repeat_all_messages(message):
#    print("Got message %s from %s id %s" % (message.text, message.from_user.first_name, message.from_user.id))
#    bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
    while True:
        print("Connecting...")
        try:
            bot.polling(none_stop=False)
        except Exception as e:
            print("Some polling error happened: {0}".format(e))
            print("Will try to reconnect in 10 seconds")
            time.sleep(10)

# Notifications are:
# ------------------------------
#
# For a regular user:
#  - motion
#  - gas / co2 / temperature / moisture by threshold

#
# Workflow
# ---------------------------------
# Superuser register itself by typing /boss
#  - if no superuser currently exists, then this users' id is saved as superuser and he gets notification
#  - if superuser exists then
#    - if it differs from current user then say 'Nope'
#	 - if it already is a boss then say 'I know' 

# When user enters any command except for `boss`, bot checks its permissions by calling `is_user_allowed(id)`
#  - if no, then reply `you are not allowed to use this bot, in order to request access type `/getaccess` and it will be reviewed by admin`
#  - if yes then execute the command

# When user types command `/getaccess` his rights are to be checked by calling `is_user_allowed(id)`
# - if user already has access then reply `access granted`
# - if user has already applied then reply `under review`. It is checked by calling method `is_access_pending(id)`
#	 - method `is_access_pending` checks if in users section [id] `status` variable equals to `pending`
# - if user was banned then reply `go away`. Is is checked by calling `is_user_banned(id)`
#	 - method `is_access_pending` checks if in users section [id] `status` variable equals to `banned`
# - if user applies for the first time then answer `please wait, your request is under review`
#	 - notify admin on such a request
#	 - create a section in config for such user [id]

# In order to grant access to user admin writes `/grant [id]`
#	- 

# Admin commands
# /boss OK
# /grant [id] OK
# /delete [id] TODO
# /ban [id] TODO
# /watch [id] TODO
# /unwatch [id] TODO
# /who? lists ids and names of users watched TODO

# Common commands
# /help
# /getaccess OK
# /photo [center, topleft, topright, bottomleft, bottomright] makes a photo PARTIAL
# /history [co2 / gas / temp / moist] [hour / {N} hours / day / week / month / year] sends a chart with data available
# /alert turns on a siren (?)
# /notify [co2 / gas / temp / moist] [less | greater] {value}
# /notify motion
# /mute [co2 / gas / temp / moist / motion]
# /what? lists my watches
