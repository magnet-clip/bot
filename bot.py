import config
import telebot
import bot_utils
import picamera
import time

bot = telebot.TeleBot(config.token)
@bot.message_handler(commands=['photo'])
def make_snapshot(message):
	file_name = "./snaps/" + bot_utils.get_temp_file_name() + ".jpg"
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

	try:
		bot.send_photo(message.chat.id, temp_file)
	except Exception as e:
		print("Failed to send photo:" + e.strerror)
	finally:
		temp_file.close()	

	try:
		bot_utils.clear_folder("./snaps")
	except Exception as e:
		print("Failed to delete temp files: " + e.strerror)


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message): 
	print("Got message " + message.text)
	bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
	while True:
		try:
			print("Connecting...")
			bot.polling(none_stop=True)
		except Exception as e:
			print("Some polling error happened: " + e.strerror)
			print("Will try to reconnect in 10 seconds")
			time.sleep(10)
		
