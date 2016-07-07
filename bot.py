import config
import telebot
import bot_utils
import picamera
import time

bot = telebot.TeleBot(config.token)
@bot.message_handler(commands=['photo'])
def make_snapshot(message):
	file_name = bot_utils.get_temp_file_name() + ".jpg"
	print("File is " + file_name)
	temp_file = open(file_name, 'wb')
	with picamera.PiCamera() as camera:
		camera.resolution = (640, 480)
		camera.start_preview()
		time.sleep(2)
		camera.capture(temp_file)
		temp_file.close()	
	print("Sending...")
	temp_file = open(file_name, 'rb')
	bot.send_photo(message.chat.id, temp_file)
	temp_file.close()	

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message): 
	bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
	bot.polling(none_stop=True)
