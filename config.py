import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """Set Flask configuration variables from .env file."""
    print("creating config")
    # General Flask Config
    FLASK_ENV = os.environ.get('FLASK_ENV')
    FLASK_APP = 'wsgi.py'
    FLASK_DEBUG = 1

    # Database
    db_host = os.environ['DB_HOST']
    db_user = os.environ['DB_USER']
    db_password = os.environ['DB_PASSWORD']
    db_schema = os.environ['DB_SCHEMA']
    SQLALCHEMY_TRACK_MODIFICATIONS = bool(os.environ["DEBUG"])
    SQLALCHEMY_DATABASE_URI = \
        'mysql+pymysql://{}:{}@{}/{}'.format(db_user, db_password, db_host, db_schema)
    SQLALCHEMY_ECHO = bool(os.environ["DEBUG"])

    # General Slack Config
    SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
    SLACK_TOKEN = os.environ['SLACK_TOKEN']
