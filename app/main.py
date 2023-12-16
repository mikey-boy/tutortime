from messages.views import messages_bp
from models import db
from sassutils.wsgi import SassMiddleware
from services.views import services_bp
from users.views import users_bp

from app import app


# app.config.from_object("config")
def main():
    app.wsgi_app = SassMiddleware(app.wsgi_app, {__name__: ("static/scss", "static/css", "static/css")})
    app.config.from_object("config")

    app.register_blueprint(services_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(messages_bp)
    with app.app_context():
        db.create_all()


main()
