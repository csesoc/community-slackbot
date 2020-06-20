# Import flask
from flask import Flask

# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Define the WSGI application object
app = Flask(__name__)

# Configurations
from config import Config
app.config.from_object('config.Config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# Import Flask-Migrate and intialise it
from flask_migrate import Migrate
migrate = Migrate()
migrate.init_app(app, db)

# Import SlackEventsAdapter and set it up
from slackeventsapi import SlackEventAdapter
slack_events_adapter = SlackEventAdapter(Config.SLACK_SIGNING_SECRET, "/slack/events", server=app)

# Set up the slack client
from slack import WebClient
client = WebClient(Config.SLACK_TOKEN)

# Import a module using its blueprint handler variable
from app.slack_server import slack

# Register blueprint
app.register_blueprint(slack)

# Build the database:
# This will create the database file using SQLAlchemy
db.create_all()