# Imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# Initialize the app
app = Flask(__name__, instance_relative_config=True)


# Load the config
app.config.from_object('config')


# Fix jinja spacing
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True


# Define the database object
db = SQLAlchemy(app)


# Load the views
from app import views
