import unittest
import confmanager
import os


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.man = confmanager.ConfManager("test.config")

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


if __name__ == '__main__':
    unittest.main()
