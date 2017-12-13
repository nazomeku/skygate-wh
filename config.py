# Define the application directory
from os import path
BASE_DIR = path.abspath(path.dirname(__file__))


# Enable DEBUG mode
DEBUG = True


# Define the database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(BASE_DIR, 'wh.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
