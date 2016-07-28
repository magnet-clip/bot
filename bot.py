import config
import telebot
import confmanager
import camera
import handler
import time
import logging
import sys
import signal
import re


def ctrl_c_handler(signum, frame):
    print("Bye!")
    sys.exit()


signal.signal(signal.SIGINT, ctrl_c_handler)

logger = telebot.logger
telebot.logger.setLevel(logging.WARN)

man = confmanager.ConfManager()
bot = telebot.TeleBot(config.token, threaded=False)
cam = camera.Camera()

bot_handler = handler.Handler(bot, man, cam)
user_message_re = "^/(ban|delete|grant) *(\d+)$"


# @bot.inline_handler(lambda query: len(query.query) > 0)
# def inline_handler(query):
#	res = telebot.types.InlineQueryResultArticle( '1','Answer', telebot.types.InputTextMessageContent(query.query))
#	bot.answer_inline_query(query.id, [res])

@bot.message_handler(commands=['boss'])
def set_boss(message):
    bot_handler.set_boss(message)


@bot.message_handler(commands=['resign'])
def resign(message):
    bot_handler.resign(message)


@bot.message_handler(commands=['getaccess'])
def get_access(message):
    bot_handler.get_access(message)


@bot.message_handler(regexp=user_message_re)
def handle_user_command(message):
    pattern = re.compile(user_message_re)
    matches = re.findall(pattern, message.text)
    print(matches)

    if matches[0][0] == 'grant':
        bot_handler.grant_access(message, matches[0][1])
    elif matches[0][0] == 'delete':
        bot_handler.delete_user(message, matches[0][1])
    elif matches[0][0] == 'ban':
        bot_handler.ban_user(message, matches[0][1])


@bot.message_handler(commands=['photo'])
def make_snapshot(message):
    bot_handler.make_snapshot(message)


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
# /watch [id] TODO
# /unwatch [id] TODO
# /who? lists ids and names of users watched TODO

# Common commands
# /help
# /photo [center, topleft, topright, bottomleft, bottomright] makes a photo PARTIAL
# /history [co2 / gas / temp / moist] [hour / {N} hours / day / week / month / year] sends a chart with data available
# /alert turns on a siren (?)
# /notify [co2 / gas / temp / moist] [less | greater] {value}
# /notify motion
# /mute [co2 / gas / temp / moist / motion]
# /what? lists my watches
