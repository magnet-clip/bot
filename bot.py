import config
import telebot
import socket

bot = telebot.TeleBot(config.token)
@bot.message_handler(commands=['ip'])
def reveal_ip(message):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("ya.ru", 80))
	
	bot.send_message(message.chat.id, s.getsockname()[0])
	s.close()

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message): 
	bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
	bot.polling(none_stop=True)
