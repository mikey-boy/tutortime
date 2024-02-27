import os


class Config(object):
    pass


class DevelopmentConfig(Config):
    # --------- CHANGE ME --------- #
    SECRET_KEY = "racecar"
    FACEBOOK_OAUTH = {
        "client_id": os.environ["FACEBOOK_CLIENT_ID"],
        "client_secret": os.environ["FACEBOOK_CLIENT_SECRET"],
    }
    GOOGLE_OAUTH = {
        "client_id": os.environ["GOOGLE_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
    }
    # ----------------------------- #

    IMAGE_FOLDER = "static/uploads"
    SQLALCHEMY_DATABASE_URI = "sqlite:///project.db"
