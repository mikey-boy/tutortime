import calendar
import json
from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from flask import (Flask, abort, jsonify, redirect, render_template, request,
                   session)
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from sassutils.wsgi import SassMiddleware
from utils import availability_to_int, availability_to_list

from database import Database, LessonStatus, ServiceStatus
from image_server import ImageServer

app = Flask(__name__)
app.config.from_object("config")
app.wsgi_app = SassMiddleware(app.wsgi_app, {__name__: ("static/scss", "static/css", "/static/css")})

db = Database(db_folder=app.config["DB_FOLDER"], user_db=app.config["USER_DB"], service_db=app.config["SERVICE_DB"])
image_server = ImageServer(image_folder=app.config["IMAGE_FOLDER"])

socketio = SocketIO(app, logger=True)

if __name__ == "__main__":
    socketio.run(app, debug=True)


@app.route("/about")
def about():
    return render_template("about.html")



