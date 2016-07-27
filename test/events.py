import os
import unittest
from unittest.mock import Mock
from handler import Handler
from confmanager import ConfManager
from dictate import Dictate


class EventsTest(unittest.TestCase):
    def tearDown(self):
        os.unlink('./temp.config')

    def test_set_new_boss(self):
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
        bot.send_message.assert_called_with('1', "You are the king now")

    def test_set_new_boss_twice(self):
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
        handler.set_boss(message)
        self.assertEqual(bot.send_message.call_count, 2)
        bot.send_message.assert_called_with('1', "I know")

    def test_set_new_boss_when_one_exists(self):
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

        message = Dictate({
            'from_user': {
                'first_name': 'L',
                'id': '13'
            },
            'chat': {
                'id': '2'
            }
        })
        handler.set_boss(message)
        self.assertEqual(bot.send_message.call_count, 2)
        bot.send_message.assert_called_with('2', "Nope")


if __name__ == '__main__':
    unittest.main()
