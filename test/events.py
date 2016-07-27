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

    def test_set_boss_and_resign(self):
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
        self.assertTrue(man.has_super_user())

        message = Dictate({
            'from_user': {
                'first_name': 'R',
                'id': '12'
            },
            'chat': {
                'id': '1'
            }
        })
        handler.resign(message)
        self.assertEqual(bot.send_message.call_count, 2)
        bot.send_message.assert_called_with('1', "We have a vacancy now")
        self.assertFalse(man.has_super_user())

    def test_set_boss_and_resign_from_other(self):
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
        handler.resign(message)
        self.assertEqual(bot.send_message.call_count, 1)
        self.assertTrue(man.has_super_user())
        self.assertEqual(man.get_admin_id(), '12')

    def test_simple_grant_access_request(self):
        bot = Mock()
        man = ConfManager('temp.config')
        cam = Mock()

        handler = Handler(bot, man, cam)

        # set admin
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

        # request access
        message = Dictate({
            'from_user': {
                'username': 'Vova',
                'first_name': 'L',
                'id': '13'
            },
            'chat': {
                'id': '2'
            },
            'text': '/getaccess'
        })
        handler.get_access(message)
        bot.send_message.assert_called_with('12', "User L id [13] wants to get access; Type /grant13 to allow, /ban13 to ban him")
        bot.send_message.assert_any_call('13', "Your application is under review")
        self.assertEqual(bot.send_message.call_count, 3)

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
        handler.grant_access(message)
        bot.send_message.assert_called_with('13', "Willkommen!")
        self.assertEqual(bot.send_message.call_count, 4)

    def test_wrong_grant_command(self):
        bot = Mock()
        man = ConfManager('temp.config')
        cam = Mock()

        handler = Handler(bot, man, cam)

        # set admin
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
        handler.grant_access(message)
        bot.send_message.assert_called_with('2', "Failed to fetch user id")
        self.assertEqual(bot.send_message.call_count, 2)

    def test_wrong_grant_access_nouser(self):
        bot = Mock()
        man = ConfManager('temp.config')
        cam = Mock()

        handler = Handler(bot, man, cam)

        # set admin
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
        handler.grant_access(message)
        bot.send_message.assert_called_with('12', "Failed to grant access")


if __name__ == '__main__':
    unittest.main()
