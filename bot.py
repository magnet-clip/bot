import config
import time
import logging
import sys
import re

from bot_manager import BotManager as MessageHandler
from signal import signal
from arduino import SerialHandler
from queue import Queue
from serial import Serial
from camera import Camera
from conf_manager import ConfManager
from db_manager import DatabaseManager
from measures import Measures as measures

try:
    import telebot
except ImportError as e:
    telebot = None

message_queue = Queue()

db = DatabaseManager()
conn = Serial(port='/dev/ttyUSB0', baudrate=38400, timeout=0.5)
sh = SerialHandler(conn, db, message_queue)
sh.start()


def ctrl_c_handler(signum, frame):
    sh.interrupt()
    print("Bye!")
    sys.exit()


signal(signal.SIGINT, ctrl_c_handler)

logger = telebot.logger
telebot.logger.setLevel(logging.WARN)

man = ConfManager()
bot = telebot.TeleBot(config.token, threaded=False)
cam = Camera()

bot_handler = MessageHandler(bot, man, cam, db)
user_message_re = "^/(ban|delete|grant) *(\d+)$"
list_users_re = "/list(g|p|b|)"
show_chart = "/show +(t|temp|temperature|h|hum|humidity|co|co2|gas|l|light)"


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

    match = matches[0]
    cmd = match[0]
    uuid = match[1]

    if cmd == 'grant':
        bot_handler.grant_access(message, uuid)
    elif cmd == 'delete':
        bot_handler.delete_user(message, uuid)
    elif cmd == 'ban':
        bot_handler.ban_user(message, uuid)


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


@bot.message_handler(regexp=show_chart)
def show_the_chart(message):
    pattern = re.compile(show_chart)
    print(show_chart)
    matches = re.findall(pattern, message.text)

    print(matches)
    var_name = matches[0]
    if var_name == 'co' or var_name == 'co2':
        field = measures.CO2
    elif var_name == 'g' or var_name == 'gas':
        field = measures.GAS
    elif var_name == 't' or var_name == 'temp' or var_name == 'temperature':
        field = measures.TEMPERATURE
    elif var_name == 'h' or var_name == 'hum' or var_name == 'humidity':
        field = measures.HUMIDITY
    elif var_name == 'l' or var_name == 'light':
        field = measures.LIGHT
    else:
        bot_handler.answer(message, "Wrong field")
        return

    bot_handler.make_and_send_plot(message, field)


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
# /current - table with current temperature/humidity etc (maybe with stats also)
# /photo [center, topleft, topright, bottomleft, bottomright] makes a photo PARTIAL
# /history [co2 / gas / temp / moist] [hour / {N} hours / day / week / month / year] sends a chart with data available
# /alert turns on a siren (?)
# /notify [co2 / gas / temp / moist / noise] [less | greater] {value}
# /notify motion
# /mute [co2 / gas / temp / moist / motion / noise]
# /what? lists my watches
