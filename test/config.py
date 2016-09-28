import unittest
import conf_manager
import os
from measures import Measures


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.man = conf_manager.ConfManager("test.config")

    def tearDown(self):
        os.unlink("./test.config")

    def test_no_super_user_initially(self):
        man = self.man
        self.assertFalse(man.has_super_user())

    def test_knows_duplicate_superuser(self):
        man = self.man
        self.assertEqual(man.set_super_user(111), man.DONE)
        self.assertEqual(man.get_admin_id(), '111')
        self.assertTrue(man.has_super_user())
        self.assertEqual(man.set_super_user(111), man.OK)
        self.assertTrue(man.has_super_user())

    def test_cant_set_another_superuser(self):
        man = self.man
        self.assertEqual(man.set_super_user(111), man.DONE)
        self.assertTrue(man.has_super_user())
        self.assertEqual(man.set_super_user(112), man.FAIL)
        self.assertTrue(man.has_super_user())
        self.assertEqual(man.get_admin_id(), '111')

    def test_delete_superuser(self):
        man = self.man
        self.assertEqual(man.set_super_user(111), man.DONE)
        self.assertTrue(man.has_super_user())
        man.dispose_super_user()
        self.assertFalse(man.has_super_user())
        self.assertEqual(man.get_admin_id(), 'NONE')

    def test_non_existing_user_does_not_exists(self):
        man = self.man
        self.assertFalse(man.user_exists('no_such_user'))
        self.assertFalse(man.is_user_pending('no_such_user'))
        self.assertFalse(man.is_user_banned('no_such_user'))

    def test_can_register_user(self):
        man = self.man
        man.register_user_pending('a_user')
        self.assertTrue(man.user_exists('a_user'))
        self.assertTrue(man.is_user_pending('a_user'))

    def test_can_delete_user(self):
        man = self.man
        man.register_user_pending('a_user')
        man.delete_user('a_user')
        self.assertFalse(man.user_exists('a_user'))

    def test_can_grant_ban_user(self):
        man = self.man
        man.register_user_pending('a_user')
        man.grant_access('a_user')
        self.assertTrue(man.user_exists('a_user'))
        self.assertFalse(man.is_user_pending('a_user'))
        self.assertFalse(man.is_user_banned('a_user'))
        man.ban_user('a_user')
        self.assertTrue(man.user_exists('a_user'))
        self.assertFalse(man.is_user_pending('a_user'))
        self.assertTrue(man.is_user_banned('a_user'))

    def test_list_users(self):
        man = self.man
        self.assertEqual(len(man.list_banned()), 0)
        self.assertEqual(len(man.list_granted()), 0)
        self.assertEqual(len(man.list_pending()), 0)

        man.register_user_pending(1, "pending")
        self.assertEqual(len(man.list_banned()), 0)
        self.assertEqual(len(man.list_granted()), 0)
        self.assertEqual(len(man.list_pending()), 1)

        man.grant_access(1)
        self.assertEqual(len(man.list_banned()), 0)
        self.assertEqual(len(man.list_granted()), 1)
        self.assertEqual(len(man.list_pending()), 0)

        man.register_user_pending(2, "pending")
        man.ban_user(2)
        self.assertEqual(len(man.list_banned()), 1)
        self.assertEqual(len(man.list_granted()), 1)
        self.assertEqual(len(man.list_pending()), 0)

        man.register_user_pending(3, "pending")
        man.delete_user(2)
        self.assertEqual(len(man.list_banned()), 0)
        self.assertEqual(len(man.list_granted()), 1)
        self.assertEqual(len(man.list_pending()), 1)

        man.delete_user(3)
        self.assertEqual(len(man.list_banned()), 0)
        self.assertEqual(len(man.list_granted()), 1)
        self.assertEqual(len(man.list_pending()), 0)

        man.delete_user(1)
        self.assertEqual(len(man.list_banned()), 0)
        self.assertEqual(len(man.list_granted()), 0)
        self.assertEqual(len(man.list_pending()), 0)

    def test_non_existing_user_has_no_notification(self):
        man = self.man
        self.assertFalse(man.has_notification(1, "xxx"))

    def test_non_existing_user_wont_add_notification(self):
        man = self.man
        man.add_notification(1, Measures.CO2, "greater", 100)
        self.assertFalse(man.has_notification(1, Measures.CO2))

    def test_existing_user_has_no_notification(self):
        man = self.man
        man.register_user_pending(1, "pending")
        self.assertTrue(man.user_exists(1))
        man.grant_access(1)
        self.assertTrue(man.is_user_allowed(1))
        self.assertTrue(man.is_user_granted(1)) # todo what's difference between granted and allowed?
        self.assertFalse(man.has_notification(1, "xxx"))

    def test_add_notification(self):
        man = self.man
        man.register_user_pending(1, "pending")
        man.grant_access(1)
        self.assertFalse(man.has_notification(1, Measures.CO2))
        man.add_notification(1, Measures.CO2, "greater", 100)
        self.assertTrue(man.has_notification(1, Measures.CO2))

    def test_add_wrong_notification(self):
        man = self.man
        man.register_user_pending(1, "pending")
        man.grant_access(1)
        self.assertFalse(man.has_notification(1, "XXX"))
        man.add_notification(1, "XXX", "greater", 100)
        self.assertFalse(man.has_notification(1, "XXX"))

    def test_remove_notification(self):
        man = self.man
        man.register_user_pending(1, "pending")
        man.grant_access(1)
        man.add_notification(1, Measures.CO2, "greater", 100)
        man.remove_notification(1, Measures.CO2)
        self.assertFalse(man.has_notification(1, Measures.CO2))

    def test_add_remove_two_notifications(self):
        man = self.man
        man.register_user_pending(1, "pending")
        man.grant_access(1)
        man.add_notification(1, Measures.CO2, "greater", 300)
        man.add_notification(1, Measures.CO2, "less", 100)
        self.assertTrue(man.has_notification(1, Measures.CO2))
        man.remove_notification(1, Measures.CO2)
        self.assertFalse(man.has_notification(1, Measures.CO2))

    def test_update_notification_does_not_fail(self):
        man = self.man
        man.register_user_pending(1, "pending")
        man.grant_access(1)
        man.add_notification(1, Measures.CO2, "greater", 300)
        man.add_notification(1, Measures.CO2, "greater", 200)
        self.assertTrue(man.has_notification(1, Measures.CO2))

    def test_non_existing_user_has_notifications_muted(self):
        man = self.man
        self.assertFalse(man.is_notification_enabled(1, "xxx"))

    def test_new_existing_users_has_notifications_muted(self):
        man = self.man
        man.register_user_pending(1, "pending")
        man.grant_access(1)
        self.assertFalse(man.is_notification_enabled(1, "xxx"))

    def test_add_notification_and_mute_it(self):
        man = self.man
        man.register_user_pending(1, "pending")
        man.grant_access(1)
        self.assertFalse(man.is_notification_enabled(1, Measures.CO2))
        self.assertTrue(man.add_notification(1, Measures.CO2, "greater", 300))
        self.assertTrue(man.is_notification_enabled(1, Measures.CO2))
        man.mute_notification(1, Measures.CO2)
        self.assertFalse(man.is_notification_enabled(1, Measures.CO2))

    def test_mute_unmute_notification(self):
        man = self.man
        man.register_user_pending(1, "pending")
        man.grant_access(1)
        man.add_notification(1, Measures.CO2, "greater", 300)
        man.mute_notification(1, Measures.CO2)
        self.assertFalse(man.is_notification_enabled(1, Measures.CO2))
        man.unmute_notification(1, Measures.CO2)
        self.assertTrue(man.is_notification_enabled(1, Measures.CO2))

    def test_mute_twice_unmute_twice(self):
        man = self.man
        man.register_user_pending(1, "pending")
        man.grant_access(1)
        man.add_notification(1, Measures.CO2, "greater", 300)
        self.assertTrue(man.is_notification_enabled(1, Measures.CO2))
        man.mute_notification(1, Measures.CO2)
        self.assertFalse(man.is_notification_enabled(1, Measures.CO2))
        man.mute_notification(1, Measures.CO2)
        self.assertFalse(man.is_notification_enabled(1, Measures.CO2))
        man.unmute_notification(1, Measures.CO2)
        self.assertTrue(man.is_notification_enabled(1, Measures.CO2))
        man.unmute_notification(1, Measures.CO2)
        self.assertTrue(man.is_notification_enabled(1, Measures.CO2))

    def test_mute_one_unmute_all(self):
        man = self.man
        man.register_user_pending(1, "pending")
        man.grant_access(1)
        man.add_notification(1, Measures.CO2, "greater", 300)
        man.add_notification(1, Measures.HUMIDITY, "greater", 100)
        self.assertTrue(man.is_notification_enabled(1, Measures.HUMIDITY))
        man.mute_notification(1, Measures.HUMIDITY)
        self.assertFalse(man.is_notification_enabled(1, Measures.HUMIDITY))
        man.unmute_all_notifications(1)
        self.assertTrue(man.is_notification_enabled(1, Measures.HUMIDITY))

    def test_mute_all_unmute_one(self):
        man = self.man
        man.register_user_pending(1, "pending")
        man.grant_access(1)
        man.add_notification(1, Measures.CO2, "greater", 300)
        man.add_notification(1, Measures.HUMIDITY, "greater", 100)
        self.assertTrue(man.is_notification_enabled(1, Measures.CO2))
        self.assertTrue(man.is_notification_enabled(1, Measures.HUMIDITY))
        man.mute_all_notifications(1)
        self.assertFalse(man.is_notification_enabled(1, Measures.CO2))
        self.assertFalse(man.is_notification_enabled(1, Measures.HUMIDITY))
        man.unmute_notification(1, Measures.CO2)
        self.assertTrue(man.is_notification_enabled(1, Measures.CO2))
        self.assertFalse(man.is_notification_enabled(1, Measures.HUMIDITY))
        man.unmute_notification(1, Measures.HUMIDITY)
        self.assertTrue(man.is_notification_enabled(1, Measures.CO2))
        self.assertTrue(man.is_notification_enabled(1, Measures.HUMIDITY))

    def test_mute_all_unmute_all(self):
        man = self.man
        man.register_user_pending(1, "pending")
        man.grant_access(1)
        man.add_notification(1, Measures.CO2, "greater", 300)
        man.add_notification(1, Measures.HUMIDITY, "greater", 100)
        self.assertTrue(man.is_notification_enabled(1, Measures.CO2))
        self.assertTrue(man.is_notification_enabled(1, Measures.HUMIDITY))
        man.mute_all_notifications(1)
        self.assertFalse(man.is_notification_enabled(1, Measures.CO2))
        self.assertFalse(man.is_notification_enabled(1, Measures.HUMIDITY))
        man.unmute_all_notifications(1)
        self.assertTrue(man.is_notification_enabled(1, Measures.CO2))
        self.assertTrue(man.is_notification_enabled(1, Measures.HUMIDITY))
        man.mute_all_notifications(1)
        self.assertFalse(man.is_notification_enabled(1, Measures.CO2))
        self.assertFalse(man.is_notification_enabled(1, Measures.HUMIDITY))
        man.mute_all_notifications(1)
        self.assertFalse(man.is_notification_enabled(1, Measures.CO2))
        self.assertFalse(man.is_notification_enabled(1, Measures.HUMIDITY))
        man.unmute_all_notifications(1)
        self.assertTrue(man.is_notification_enabled(1, Measures.CO2))
        self.assertTrue(man.is_notification_enabled(1, Measures.HUMIDITY))
        man.unmute_all_notifications(1)
        self.assertTrue(man.is_notification_enabled(1, Measures.CO2))
        self.assertTrue(man.is_notification_enabled(1, Measures.HUMIDITY))


# more tests:
# - reading exact notification thresholds (which format??)
#

if __name__ == '__main__':
    unittest.main()
