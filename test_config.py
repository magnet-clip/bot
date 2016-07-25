import unittest
import bot_utils
import os

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.man = bot_utils.Config("test.config")
        
    def tearDown(self):
        os.unlink("./test.config")
    
    def no_super_user_initially(self):
        """No super user exists in empty config"""
        man = self.man
        self.assertFalse(man.has_super_user())
        pass
    
if __name__ == '__main__':
    unittest.main()