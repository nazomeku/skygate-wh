# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Enable DEBUG mode
DEBUG = True

# Define the database
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
