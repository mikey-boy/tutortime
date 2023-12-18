from message.views import message_bp
from models import db
from sassutils.wsgi import SassMiddleware
from service.views import service_bp
from user.views import user_bp

from app import app


# app.config.from_object("config")
def main():
    app.wsgi_app = SassMiddleware(app.wsgi_app, {__name__: ("static/scss", "static/css", "static/css")})
    app.config.from_object("config")

    app.register_blueprint(service_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(message_bp)
    with app.app_context():
        db.create_all()


main()
