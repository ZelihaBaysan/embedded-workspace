# tests/test_main.py
import unittest
from src.utils import helper_function

class TestUtils(unittest.TestCase):
    def test_helper(self):
        self.assertEqual(helper_function(), "Utility function result")

if __name__ == "__main__":
    unittest.main()