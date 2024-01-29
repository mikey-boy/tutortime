from flask_apscheduler import APScheduler
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
socketio = SocketIO()
scheduler = APScheduler()
