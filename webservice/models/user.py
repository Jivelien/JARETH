import re


class User:
    SPECIAL_CHAR = '$@#%&*!?'

    def __init__(self,
                 user_id: int = None, public_id: str = None,
                 username: str = None, mail: str = None,
                 password: str = None, hashed_password: str = None) -> None:
        self.user_id = user_id
        self.public_id = public_id
        self.username = username
        self.mail = mail
        self.password = password
        self.hashed_password = hashed_password

        self._control_username_format() if self.username else None
        self._control_mail_format() if self.mail else None
        self._control_password_format() if self.password else None

    def _control_username_format(self) -> None:
        if len(self.username) < 3 or len(self.username) > 20:
            raise ValueError('Username must be between 3 and 20 characters')
        if not bool(re.match('^[a-zA-Z0-9]*$', self.username)):
            raise ValueError('Username must contain only letters and numbers')
        if self.username[0].isdigit():
            raise ValueError('Username must not start with a number')

    def _control_mail_format(self) -> None:
        if not bool(re.match('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', self.mail)):
            raise ValueError('Mail must be a valid email address')

    def _control_password_format(self) -> None:
        if len(self.password) < 6 or len(self.password) > 20:
            raise ValueError('Password must be between 6 and 20 characters')
        if not any(char.isdigit() for char in self.password):
            raise ValueError('Password must contain at least one number')
        if not any(char.isupper() for char in self.password):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in self.password):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(char in User.SPECIAL_CHAR for char in self.password):
            raise ValueError('Password must contain at least one special character')

    def to_json(self) -> dict:
        return {
            'public_id': self.public_id,
            'username': self.username,
            'mail': self.mail
        }
