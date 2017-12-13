# Imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize the app
app = Flask(__name__, instance_relative_config=True)

# Load the views
from app import views

# Load the config file
app.config.from_object('config')

# Define the database object which is imported by modules and controllers
db = SQLAlchemy(app)

# Build the database
# db.create_all()
