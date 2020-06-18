import os

from flask import Flask, make_response, request
from flask_migrate import Migrate, Config
from flask_sqlalchemy import SQLAlchemy
from slack import WebClient
from slackeventsapi import SlackEventAdapter

from app.slack import slack

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    slack_signing_secret = os.environ['SLACK_SIGNING_SECRET']
    slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/", server=app)

    slack_token = os.environ['SLACK_TOKEN']
    client = WebClient(slack_token)

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from . import models
        app.register_blueprint(slack)
        return app


