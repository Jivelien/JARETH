import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY=os.getenv('FRONT_SECRET_KEY', 'Where is my secret key') 