class Config(object):
    pass


class DevelopmentConfig(Config):
    # --------- CHANGE ME --------- #
    SECRET_KEY = "racecar"
    FACEBOOK_OAUTH = {
        "client_id": "",
        "client_secret": "",
    }
    GOOGLE_OAUTH = {
        "client_id": "",
        "client_secret": "",
    }
    # ----------------------------- #

    IMAGE_FOLDER = "static/uploads"
    SQLALCHEMY_DATABASE_URI = "sqlite:///project.db"
