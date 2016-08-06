import config
import arduino
import telebot
import confmanager
import camera
import handler
import time
import logging
import sys
import signal
import re
import serial

conn = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=0.5)
sh = arduino.SerialHandler(conn)
sh.start()


def ctrl_c_handler(signum, frame):
    sh.interrupt()
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
list_users_re = "/list(g|p|b|)"


# @bot.inline_handler(lambda query: len(query.query) > 0)
# def inline_handler(query):
#	res = telebot.types.InlineQueryResultArticle( '1','Answer', telebot.types.InputTextMessageContent(query.query))
#	bot.answer_inline_query(query.id, [res])

# -----------------------------
# Boss-level commands
# -----------------------------
@bot.message_handler(commands=['boss'])
def set_boss(message):
    bot_handler.set_boss(message)


@bot.message_handler(commands=['resign'])
def resign(message):
    bot_handler.resign(message)


@bot.message_handler(regexp=user_message_re)
def handle_user_command(message):
    pattern = re.compile(user_message_re)
    matches = re.findall(pattern, message.text)

    if matches[0][0] == 'grant':
        bot_handler.grant_access(message, matches[0][1])
    elif matches[0][0] == 'delete':
        bot_handler.delete_user(message, matches[0][1])
    elif matches[0][0] == 'ban':
        bot_handler.ban_user(message, matches[0][1])


@bot.message_handler(regexp=list_users_re)
def handle_list_users(message):
    pattern = re.compile(list_users_re)
    matches = re.findall(pattern, message.text)

    if len(matches) > 0:
        bot_handler.list_users(message, matches[0])
    else:
        bot_handler.list_users(message, "")


# -----------------------------
# User-level commands
# -----------------------------
@bot.message_handler(commands=['getaccess'])
def get_access(message):
    bot_handler.get_access(message)


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

# Common commands
# /help
# /photo [center, topleft, topright, bottomleft, bottomright] makes a photo PARTIAL
# /history [co2 / gas / temp / moist] [hour / {N} hours / day / week / month / year] sends a chart with data available
# /alert turns on a siren (?)
# /notify [co2 / gas / temp / moist / noise] [less | greater] {value}
# /notify motion
# /mute [co2 / gas / temp / moist / motion / noise]
# /what? lists my watches
