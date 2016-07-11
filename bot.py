import config
import telebot
import bot_utils
import picamera
import time

def make_and_save_snapshot():
	file_name = "./snaps/" + bot_utils.get_temp_file_name() + ".jpg"
	print("File is " + file_name)
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
	file_name = make_and_save_snapshot()
	temp_file = open(file_name, 'rb')
	try:
		print("Sending...")
		bot.send_photo(message.chat.id, temp_file)
	except Exception as e:
		print("Failed to send photo:" + str(e))
	finally:
		temp_file.close()

	try:
		bot_utils.clear_folder("./snaps")
	except Exception as e:
		print("Failed to delete temp files: " + str(e))


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
	print("Got message " + message.text)
	bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
    try:
        print("Connecting...")
        bot.polling(none_stop=False)
    except KeyboardInterrupt:
        print("Bye!")
        interrupted = True
    except Exception as e:
        print("Some polling error happened: " + str(e))
        print("Will try to reconnect in 10 seconds")
        time.sleep(10)
