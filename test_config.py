import unittest
import bot_utils
import os

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.man = bot_utils.Config("test.config")

    def tearDown(self):
        os.unlink("./test.config")

    def test_no_super_user_initially(self):
        man = self.man
        self.assertFalse(man.has_super_user())

    def test_knows_duplicate_superuser(self):
        man = self.man
        self.assertEqual(man.set_super_user(111), man.DONE)
        self.assertTrue(man.has_super_user())
        self.assertEqual(man.set_super_user(111), man.OK)
        self.assertTrue(man.has_super_user())

    def test_cant_set_another_superuser(self):
        man = self.man
        self.assertEqual(man.set_super_user(111), man.DONE)
        self.assertTrue(man.has_super_user())
        self.assertEqual(man.set_super_user(112), man.FAIL)
        self.assertTrue(man.has_super_user())

    def test_delete_superuser(self):
        man = self.man
        self.assertEqual(man.set_super_user(111), man.DONE)
        self.assertTrue(man.has_super_user())
        man.dispose_super_user()
        self.assertFalse(man.has_super_user())

if __name__ == '__main__':
    unittest.main()
