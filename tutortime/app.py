import os

from flask import Flask
from sassutils.wsgi import SassMiddleware

from tutortime.commands import initdb
from tutortime.config import CloudDevelopmentConfig, CloudProductionConfig, LocalDevelopmentConfig
from tutortime.extensions import db, scheduler, socketio
from tutortime.user.views import configure_oauth_providers


def create_app(config=None):
    app = Flask(__name__)

    if config == "CloudDevelopmentConfig":
        configure_app(app, CloudDevelopmentConfig)
    elif config == "CloudProductionConfig":
        configure_app(app, CloudProductionConfig)
    else:
        configure_app(app, LocalDevelopmentConfig)

    if os.path.exists(app.config["IMAGE_FOLDER"]) is False:
        os.makedirs(app.config["IMAGE_FOLDER"])

    configure_extensions(app)
    configure_blueprints(app)
    create_db(app)
    configure_cli(app)
    return app


def configure_app(app, config):
    app.config.from_object(config)
    app.wsgi_app = SassMiddleware(app.wsgi_app, {__name__: ("static/scss", "static/css", "static/css")})


def configure_extensions(app):
    db.init_app(app)
    configure_oauth_providers(app)
    socketio.init_app(app, logger=True)
    scheduler.init_app(app)
    scheduler.start()


def configure_blueprints(app):
    from tutortime.message.views import message_bp
    from tutortime.service.views import service_bp
    from tutortime.user.views import user_bp

    app.register_blueprint(service_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(message_bp)


def create_db(app):
    with app.app_context():
        db.create_all()


def configure_cli(app):
    @app.cli.command("initdb")
    def initdb_cli():
        initdb()
