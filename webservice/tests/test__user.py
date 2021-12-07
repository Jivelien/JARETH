import unittest
from models.user import User


class TestUsername(unittest.TestCase):
    def test__username_can_be_created(self):
        username = "Artem"
        user = User(username=username)
        self.assertEqual(user.username, username)

    def test__username_should_be_at_least_3chars_long(self):
        with self.assertRaises(ValueError):
            User(username="a")

    def test__username_should_be_at_most_20chars_long(self):
        with self.assertRaises(ValueError):
            User(username="a" * 21)

    def test__username_should_contains_normal_chars(self):
        with self.assertRaises(ValueError):
            User(username="Artem#")

    def test__username_should_not_start_with_digit(self):
        with self.assertRaises(ValueError):
            User(username="1Artem")


class TestMail(unittest.TestCase):

    def test__mail_can_be_created(self):
        mail = "artem@gmail.com"
        user = User(mail=mail)
        self.assertEqual(user.mail, mail)

    def test__mail_should_look_like_a_mail(self):
        with self.assertRaises(ValueError):
            User(mail="artem")
        with self.assertRaises(ValueError):
            User(mail="artem@gmail")
        with self.assertRaises(ValueError):
            User(mail="gmail.com.fr")


class TestPassword(unittest.TestCase):
    PASSWORD_EXEMPLE = "@rt3mTheBest!"

    def test__password_can_be_created(self):
        user = User(password=TestPassword.PASSWORD_EXEMPLE)
        self.assertEqual(user.password, TestPassword.PASSWORD_EXEMPLE)

    def test__password_should_be_at_least_6chars_long(self):
        with self.assertRaises(ValueError):
            User(password=TestPassword.PASSWORD_EXEMPLE[:5])

    def test__password_should_be_at_most_20chars_long(self):
        with self.assertRaises(ValueError):
            User(password=TestPassword.PASSWORD_EXEMPLE * 22)

    def test__password_should_contains_a_digit(self):
        password = "".join(["a" if char.isdigit() else char for char in TestPassword.PASSWORD_EXEMPLE])
        with self.assertRaises(ValueError):
            User(password=password)

    def test__password_should_contains_a_upper_case_letter(self):
        password = TestPassword.PASSWORD_EXEMPLE.lower()
        with self.assertRaises(ValueError):
            User(password=password)

    def test__password_should_contains_a_lower_case_letter(self):
        password = TestPassword.PASSWORD_EXEMPLE.upper()
        with self.assertRaises(ValueError):
            User(password=password)

    def test__password_should_contains_a_special_char(self):
        password = "".join(["a" if not char.isalpha() and not char.isdigit() else char for char in TestPassword.PASSWORD_EXEMPLE])
        with self.assertRaises(ValueError):
            User(password=password)


if __name__ == '__main__':
    unittest.main()
