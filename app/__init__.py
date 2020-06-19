from flask_migrate import Migrate, Config
from flask_sqlalchemy import SQLAlchemy
from app.slack_server import app, slack

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    """Construct the core application."""
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from . import models
        app.register_blueprint(slack)
        return app


