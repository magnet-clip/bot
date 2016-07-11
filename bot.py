import config
import telebot
import bot_utils
import picamera
import time
import logging

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

def make_and_save_snapshot():
    file_name = "./snaps/" + bot_utils.get_temp_file_name() + ".jpg"
    logging.debug("File is %s", file_name)
    temp_file = open(file_name, 'wb')
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.start_preview()
        time.sleep(2)
        camera.capture(temp_file)
        temp_file.close()
    return file_name

bot = telebot.TeleBot(config.token, threaded=False)

@bot.inline_handler(lambda query: len(query.query) > 0)
def inline_handler(query):
	res = telebot.types.InlineQueryResultArticle( '1','Answer', telebot.types.InputTextMessageContent(query.query))
	bot.answer_inline_query(query.id, [res])

@bot.message_handler(commands=['photo'])
def make_snapshot(message):
    logging.debug("User %s requested a photo", message.from_user.first_name)
    file_name = make_and_save_snapshot()
    temp_file = open(file_name, 'rb')
    try:
        logging.debug("Sending...")
        bot.send_photo(message.chat.id, temp_file)
    except Exception as e:
        logging.error("Failed to send photo", exc_info=e)
    finally:
        temp_file.close()

    try:
        bot_utils.clear_folder("./snaps")
    except Exception as e:
        logging.error("Failed to delete temp files", exc_info=e)


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    print("Got message %s from %s", message.text, message.from_user.first_name)
    bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
    try:
        logging.info("Connecting...")
        bot.polling(none_stop=False)
    except KeyboardInterrupt:
        logging.ingo("Bye!")
        interrupted = True
    except Exception as e:
        logging.error("Some polling error happened", exc_info=e)
        logging.info("Will try to reconnect in 10 seconds")
        time.sleep(10)
