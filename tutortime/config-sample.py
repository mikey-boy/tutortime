import os


class Config(object):
    pass


class LocalDevelopmentConfig(Config):
    SECRET_KEY = "racecar"
    DATA_FOLDER = "static/"
    IMAGE_FOLDER = os.path.join(DATA_FOLDER, "uploads")
    SQLALCHEMY_DATABASE_URI = "sqlite:///tutortime.db"

    # OAuth integration won't work but local acccounts should
    FACEBOOK_OAUTH = {
        "client_id": "",
        "client_secret": "",
    }
    GOOGLE_OAUTH = {
        "client_id": "",
        "client_secret": "",
    }


class CloudDevelopmentConfig(Config):
    # Better to store as environment variable otherwise sessions will be invalidated after server restarts
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", os.urandom(16))

    # Store application data on a persistent disk in Render
    DATA_FOLDER = "/var/lib/data/tutortime/"
    IMAGE_FOLDER = os.path.join(DATA_FOLDER, "uploads")
    SQLALCHEMY_DATABASE_URI = "sqlite:////var/lib/data/tutortime/tutortime.db"

    # OAuth2 integration with various providers
    FACEBOOK_OAUTH = {
        "client_id": os.environ.get("FACEBOOK_CLIENT_ID", ""),
        "client_secret": os.environ.get("FACEBOOK_CLIENT_SECRET", ""),
    }
    GOOGLE_OAUTH = {
        "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""),
    }


class CloudProductionConfig(Config):
    pass
