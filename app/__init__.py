from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap


# Initialize the app
app = Flask(__name__, instance_relative_config=True)
Bootstrap(app)


# Load the config
app.config.from_object('config')


# Define the database object
db = SQLAlchemy(app)


# Fix jinja spacing
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True


# Import views and db_init.
from . import views, db_init

# Initialize databases.
@app.before_first_request
def setup():
    db_init.db_products_init()
    db_init.db_transports_init()
    db_init.db_shelf_init()
    #views.random_fill()
