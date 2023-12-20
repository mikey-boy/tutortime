class Config(object):
    pass


class DevelopmentConfig(Config):
    SECRET_KEY = "racecar"
    IMAGE_FOLDER = "static/uploads"
    SQLALCHEMY_DATABASE_URI = "sqlite:///project.db"
