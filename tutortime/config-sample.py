import os


class Config(object):
    pass


class DevelopmentConfig(Config):
    # Generate a new secret key if one is not present (https://flask.palletsprojects.com/en/1.1.x/quickstart/#sessions)
    # Better to store as environment variable otherwise sessions will be invalidated after server restarts
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", os.urandom(16))
    # SECRET_KEY = "racecar"    # You can also just hardcode a test value for simplicity

    # OAuth2 integration with various providers. Local credentials will still work if these are not present
    FACEBOOK_OAUTH = {
        "client_id": os.environ.get("FACEBOOK_CLIENT_ID", ""),
        "client_secret": os.environ.get("FACEBOOK_CLIENT_SECRET", ""),
    }
    GOOGLE_OAUTH = {
        "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""),
    }

    IMAGE_FOLDER = "static/uploads"
    SQLALCHEMY_DATABASE_URI = "sqlite:///project.db"
