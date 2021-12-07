import unittest
from models.user import User


class TestUsername(unittest.TestCase):

    def test__username_should_be_at_least_3chars_long(self):
        with self.assertRaises(ValueError):
            User(username="a")

    def test__username_should_be_at_most_20chars_long(self):
        with self.assertRaises(ValueError):
            User(username="a"*21)

    def test__username_should_contains_normal_chars(self):
        with self.assertRaises(ValueError):
            User(username="Artem#")

    def test__username_should_not_start_with_digit(self):
        with self.assertRaises(ValueError):
            User(username="1Artem")

    def test__username_can_be_created(self):
        username = "Artem"
        user = User(username=username)
        self.assertEqual(user.username, username)

if __name__ == '__main__':
    unittest.main()
