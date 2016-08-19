import os
import unittest
from unittest.mock import Mock, patch
from bot_manager import BotManager
from conf_manager import ConfManager
from db_manager import DatabaseManager
from dictate import Dictate


def create_objects():
    bot = Mock()
    man = ConfManager('temp.config')
    cam = Mock()
    db = DatabaseManager()
    plotter = Mock()

    handler = BotManager(bot, man, cam, db, plotter)
    return handler, bot, man, cam


def create_message(id, chat_id, name, username="", text=""):
    return Dictate({
        'from_user': {
            'first_name': name,
            'username': username,
            'id': id
        },
        'chat': {
            'id': chat_id
        },
        text: text
    })


# @patch("matplotlib.pyplot")
# @patch("picamera")
# @patch("telebot")
class EventsTest(unittest.TestCase):
    def tearDown(self):
        os.unlink('./temp.config')

    def test_set_new_boss(self):
        handler, bot, man, cam = create_objects()

        message = create_message(id='12', name='R', chat_id='1')
        handler.set_boss(message)
        self.assertTrue(bot.send_message.called)
        bot.send_message.assert_called_with('1', "You are the king now")

    def test_set_new_boss_twice(self):
        handler, bot, man, cam = create_objects()

        message = create_message(id='12', name='R', chat_id='1')
        handler.set_boss(message)
        self.assertTrue(bot.send_message.called)

        message = create_message(id='12', name='R', chat_id='1')
        handler.set_boss(message)
        self.assertEqual(bot.send_message.call_count, 2)
        bot.send_message.assert_called_with('1', "I know")

    def test_set_new_boss_when_one_exists(self):
        handler, bot, man, cam = create_objects()

        message = create_message(id='12', name='R', chat_id='1')
        handler.set_boss(message)

        message = create_message(id='13', name='L', chat_id='2')
        handler.set_boss(message)
        self.assertEqual(bot.send_message.call_count, 2)
        bot.send_message.assert_called_with('2', "Nope")

    def test_set_boss_and_resign(self):
        handler, bot, man, cam = create_objects()

        message = create_message(id='12', name='R', chat_id='1')
        handler.set_boss(message)
        self.assertTrue(man.has_super_user())

        handler.resign(message)
        self.assertEqual(bot.send_message.call_count, 2)
        bot.send_message.assert_called_with('1', "We have a vacancy now")
        self.assertFalse(man.has_super_user())

    def test_set_boss_and_resign_from_other(self):
        handler, bot, man, cam = create_objects()

        message = create_message(id='12', name='R', chat_id='1')
        handler.set_boss(message)

        message = create_message(id='13', name='L', chat_id='2')
        handler.resign(message)
        self.assertEqual(bot.send_message.call_count, 1)
        self.assertTrue(man.has_super_user())
        self.assertEqual(man.get_admin_id(), '12')

    def test_simple_grant_access_request(self):
        handler, bot, man, cam = create_objects()

        # set admin
        message = create_message(id='12', name='R', chat_id='1')
        handler.set_boss(message)

        # request access
        message = create_message(id='13', name='L', username='Vova', chat_id='2', text="/getaccess")
        handler.get_access(message)
        bot.send_message.assert_called_with('12',
                                            "User L id [13] wants to get access; "
                                            "Type /grant13 to allow, /ban13 to ban him")
        bot.send_message.assert_any_call('13', "Your application is under review")
        self.assertEqual(bot.send_message.call_count, 3)

        # and grant access
        message = create_message(id='12', name='R', chat_id='1', text="/grant13")
        handler.grant_access(message, '13')
        bot.send_message.assert_called_with('13', "Willkommen!")
        self.assertEqual(bot.send_message.call_count, 4)

    def test_wrong_grant_command(self):
        handler, bot, man, cam = create_objects()

        # set admin
        message = create_message(id='12', name='R', chat_id='1')
        handler.set_boss(message)

        # sent wrong grant message
        message = Dictate({
            'from_user': {
                'first_name': 'R',
                'id': '12'
            },
            'chat': {
                'id': '2'
            },
            'text': '/grant'
        })
        handler.grant_access(message, '12')
        bot.send_message.assert_called_with('12', "Failed to grant access")
        self.assertEqual(bot.send_message.call_count, 2)

    def test_wrong_grant_access_no_user(self):
        handler, bot, man, cam = create_objects()

        # set admin
        message = create_message(id='12', name='R', chat_id='1')
        handler.set_boss(message)

        # and grant access
        message = Dictate({
            'from_user': {
                'first_name': 'R',
                'id': '12'
            },
            'chat': {
                'id': '2'
            },
            'text': '/grant13'
        })
        handler.grant_access(message, '12')
        bot.send_message.assert_called_with('12', "Failed to grant access")

    def test_unauthorized_user_takes_photo(self):
        handler, bot, man, cam = create_objects()

        message = create_message(id='12', name='R', chat_id='1')
        handler.make_snapshot(message)
        cam.make_and_save_snapshot.assert_not_called()
        bot.send_photo.assert_not_called()
        bot.send_message.assert_called_with('1', "You have to be authorized to request photo")

    def test_authorized_user_takes_photo(self):
        handler, bot, man, cam = create_objects()

        message = create_message(id='12', name='R', chat_id='1')
        handler.set_boss(message)
        message = create_message(id='13', name='L', username='Vova', chat_id='2', text="/getaccess")
        handler.get_access(message)
        message = create_message(id='12', name='R', chat_id='1', text='/grant13')
        handler.grant_access(message, '13')
        bot.send_message.reset_mock()
        message = create_message(id='13', name='L', chat_id='2', text="/photo")
        handler.make_snapshot(message)
        self.assertEqual(cam.make_and_save_snapshot.call_count, 1)
        bot.send_message.assert_called_with('2', 'Failed to send a photo :(')


if __name__ == '__main__':
    unittest.main()
