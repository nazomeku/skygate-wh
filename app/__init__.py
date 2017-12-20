# Imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap


# Initialize the app
app = Flask(__name__, instance_relative_config=True)


# Load the config
app.config.from_object('config')


# Fix jinja spacing
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True


# Define the database object
db = SQLAlchemy(app)
Bootstrap(app)


# Load the views and models
from app import views, models


# Transports table init.
def db_transports_init():
    all_transports = models.Transport.query.all()
    if len(all_transports) < 10:
        for _ in range(1, 11):
            transport = models.Transport(product_name=None, product_id=None)
            db.session.add(transport)
        db.session.commit()


# Shelfs table init.
def db_shelf_init():
    all_shelfs = models.Shelf.query.all()
    if len(all_shelfs) < 100:
        for _ in range(1, 101):
            shelf = models.Shelf(product_id=None)
            db.session.add(shelf)
        db.session.commit()


db_transports_init()
db_shelf_init()
