import os
import unittest
from unittest.mock import Mock
from handler import Handler
from confmanager import ConfManager
from dictate import Dictate

class EventsTest(unittest.TestCase):
    def tearDown(self):
        os.unlink('./temp.config')

    def test_simple(self):
        bot = Mock()
        man = ConfManager('temp.config')
        cam = Mock()
        handler = Handler(bot, man, cam)

        message = Dictate({
            'from_user': {
                'first_name': 'R',
                'id': '12'
            },
            'chat': {
                'id': '1'
            }
        })

        handler.set_boss(message)
        self.assertTrue(bot.send_message.called)


if __name__ == '__main__':
    unittest.main()
