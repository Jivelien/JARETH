import re


class User:
    SPECIAL_CHAR = '$@#%&*!?'

    def __init__(self,
                 user_id: int = None, public_id: str = None,
                 username: str = None, mail: str = None,
                 password: str = None, hashed_password: str = None) -> None:
        self.user_id = None
        self.public_id = None
        self.username = None
        self.mail = None
        self.password = None
        self.hashed_password = None

        self.set_public_id(public_id=public_id)
        self.set_username(username=username)
        self.set_mail(mail=mail)
        self.set_password(password=password)

    def set_user_id(self, user_id: int) -> None:
        self.user_id = user_id

    def set_public_id(self, public_id: str) -> None:
        self.public_id = public_id

    def set_username(self, username: str) -> None:
        if len(username) < 3 or len(username) > 20:
            raise ValueError('Username must be between 3 and 20 characters')
        if not bool(re.match('^[a-zA-Z0-9]*$', username)):
            raise ValueError('Username must contain only letters and numbers')
        if username[0].isdigit():
            raise ValueError('Username must not start with a number')

        self.username = username

    def set_mail(self, mail: str) -> None:
        # if not bool(re.match('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', mail)):
        #     raise ValueError('Mail must be a valid email address')
        self.mail = mail

    def set_password(self, password: str) -> None:
        # if len(password) < 6 or len(password) > 20:
        #     raise ValueError('Password must be between 6 and 20 characters')
        # if not any(char.isdigit() for char in password):
        #     raise ValueError('Password must contain at least one number')
        # if not any(char.isupper() for char in password):
        #     raise ValueError('Password must contain at least one uppercase letter')
        # if not any(char.islower() for char in password):
        #     raise ValueError('Password must contain at least one lowercase letter')
        # if not any(char in User.SPECIAL_CHAR for char in password):
        #     raise ValueError('Password must contain at least one special character')
        self.password = password

    def to_json(self) -> dict:
        return {
            'public_id': self.public_id,
            'username': self.username,
            'mail': self.mail,
            'password': self.password
        }
