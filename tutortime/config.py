class Config(object):
    pass


class DevelopmentConfig(Config):
    SECRET_KEY = "racecar"
    IMAGE_FOLDER = "static/uploads"
    SQLALCHEMY_DATABASE_URI = "sqlite:///project.db"
    FACEBOOK_OAUTH = {
        "client_id": "",
        "client_secret": "",
    }
    GOOGLE_OAUTH = {
        "client_id": "",
        "client_secret": "",
    }
