from flask import Flask
from sassutils.wsgi import SassMiddleware

from tutortime.config import DevelopmentConfig
from tutortime.extensions import db, socketio


def create_app():
    app = Flask(__name__)
    configure_app(app, DevelopmentConfig)
    configure_extensions(app)
    configure_blueprints(app)
    test(app)
    return app


def configure_app(app, config):
    app.config.from_object(config)
    app.wsgi_app = SassMiddleware(app.wsgi_app, {__name__: ("static/scss", "static/css", "static/css")})


def configure_extensions(app):
    db.init_app(app)

    socketio.init_app(app, logger=True)


def configure_blueprints(app):
    from tutortime.message.views import message_bp
    from tutortime.service.views import service_bp
    from tutortime.user.views import user_bp

    app.register_blueprint(service_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(message_bp)


def test(app):
    with app.app_context():
        db.create_all()
