import unittest
from unittest.mock import Mock
import bot_events
import bot_utils

class EventsTest(unittest.TestCase):
    def test_simple(self):
        bot = Mock()
        man = bot_utils.Config('temp.config')
        cam = Mock()
        handler = bot_events.Handler(bot, man, cam)
        message = type('', (), {})()
        message.from_user = type('', (), {})()
        message.chat = type('', (), {})()
        message.from_user.first_name = 'R'
        message.from_user.id = '12'
        message.chat.id = '13'
        handler.set_boss(message)
        self.assertTrue(bot.send_message.called)

if __name__ == '__main__':
    unittest.main()
