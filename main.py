import calendar
import json
from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from flask import Flask, abort, jsonify, redirect, render_template, request, session
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


@app.route("/user/calendar/list")
def user_calendar_list():
    if "username" not in session:
        return render_template("error/not_logged_in.html")

    lessons = db.get_lessons_for_user(session["userId"])
    for lesson in lessons:
        lesson["dt"] = datetime.strptime(lesson["datetime"], "%Y-%m-%dT%H:%M")
        if session["userId"] == lesson["tutorId"]:
            lesson["tutorName"] = session["username"]
            lesson["studentName"] = db.get_username(lesson["studentId"])
        else:
            lesson["tutorName"] = db.get_username(lesson["tutorId"])
            lesson["studentName"] = session["username"]

    cal = []
    today = date.today()
    for i in range(-12, 13):
        cur_month = today + relativedelta(months=i)
        monthrange = calendar.monthrange(cur_month.year, cur_month.month)
        month = {}
        month["year"] = cur_month.year
        month["month_name"] = calendar.month_name[cur_month.month]
        month["month_offset"] = monthrange[0]
        month["month_length"] = monthrange[1]
        month["lessons"] = []
        for lesson in lessons:
            if cur_month.month == lesson["dt"].month and cur_month.year == lesson["dt"].year:
                lesson["day"] = lesson["dt"].day
                lesson["start_time"] = datetime.strftime(lesson["dt"], "%H:%M")
                lesson["end_time"] = datetime.strftime(
                    lesson["dt"] + relativedelta(minutes=lesson["proposedDurationMinutes"]), "%H:%M"
                )
                lesson["title"] = lesson["title"]
                lesson["is_tutor"] = lesson["tutorName"] == session["username"]
                month["lessons"].append(lesson)

        cal.append(month)

    return render_template("user/calendar/list.html", lessons=lessons, calendar=cal, today=today.day)


@socketio.on("createLesson")
def create_lesson(payload):
    user_id = session["userId"]
    peer_id = payload["peerId"]
    service_id = payload["serviceId"]
    dt = f"{payload['date']}T{payload['time']}"
    duration = payload["duration"]

    service = db.get_service_by_id(service_id)
    if service["userId"] == user_id:
        status = LessonStatus.ACCEPTED_TUTOR
        lesson_id = db.add_lesson(service_id, user_id, peer_id, status, dt, duration)
    else:
        status = LessonStatus.ACCEPTED_STUDENT
        lesson_id = db.add_lesson(service_id, peer_id, user_id, status, dt, duration)

    db.add_message(session["room"], user_id, peer_id, dt, "", lesson_id)
    lesson = {
        "sender": session["username"],
        "senderId": user_id,
        "message": "",
        "lessonId": lesson_id,
        "serviceTitle": service["title"],
        "day": payload["date"],
        "time": payload["time"],
        "duration": duration,
        "status": status,
    }
    emit("createLesson", lesson, to=session["room"])


def _user_lesson_modify(lesson, accepted_states):
    if "username" not in session:
        abort(401)
    if session["userId"] not in [lesson["tutorId"], lesson["studentId"]]:
        abort(403)
    if lesson["status"] not in accepted_states:
        abort(403)


def _system_message(lesson, status):
    dt = datetime.strptime(lesson["datetime"], "%Y-%m-%dT%H:%M")
    day = dt.strftime("%Y-%m-%d")
    time = dt.strftime("%H:%M")
    service = db.get_service_by_id(lesson["serviceId"])
    if status == LessonStatus.ACCEPTED:
        message = f"{session['username']} accepted '{service['title']}' scheduled for {day} @ {time}"
    elif status == LessonStatus.CANCELLED:
        message = f"{session['username']} cancelled '{service['title']}' scheduled for {day} @ {time}"
    else:
        message = f"{session['username']} confirmed '{service['title']}' on {day} @ {time} for {lesson['actualDurationMinutes']} minutes"

    now = datetime.now().strftime("%Y-%m-%dT%H:%M")
    db.add_message(session["room"], -1, -1, now, message)


@socketio.on("modifyLesson")
def modify_lesson(payload):
    lesson = db.get_lesson_request(payload["lessonId"])
    _user_lesson_modify(lesson, [LessonStatus.ACCEPTED_STUDENT, LessonStatus.ACCEPTED_TUTOR])

    dt = f"{payload['date']}T{payload['time']}"
    duration = payload["duration"]
    if lesson["tutorId"] == session["userId"]:
        db.update_lesson(lesson["id"], dt, duration, LessonStatus.ACCEPTED_TUTOR)
    else:
        db.update_lesson(lesson["id"], dt, duration, LessonStatus.ACCEPTED_STUDENT)

    message = db.get_message_by_lesson_id(lesson["id"])
    db.update_message(message["id"], session["userId"], payload["peerId"])
    emit("pageReload", to=session["room"])


@socketio.on("acceptLesson")
def accept_lesson(payload):
    lesson = db.get_lesson_request(payload["lessonId"])
    _user_lesson_modify(lesson, [LessonStatus.ACCEPTED_STUDENT, LessonStatus.ACCEPTED_TUTOR])
    if lesson["status"] == LessonStatus.ACCEPTED_STUDENT and lesson["studentId"] == session["userId"]:
        abort(403)
    if lesson["status"] == LessonStatus.ACCEPTED_TUTOR and lesson["tutorId"] == session["userId"]:
        abort(403)

    db.update_lesson_status(lesson["id"], LessonStatus.ACCEPTED)
    db.update_user_balance(lesson["studentId"], lesson["proposedDurationMinutes"] * -1)
    _system_message(lesson, LessonStatus.ACCEPTED)
    emit("pageReload", to=session["room"])


@socketio.on("confirmLesson")
def confirm_lesson(payload):
    lesson = db.get_lesson_request(payload["lessonId"])
    _user_lesson_modify(lesson, [LessonStatus.ACCEPTED, LessonStatus.CONFIRMED_STUDENT, LessonStatus.CONFIRMED_TUTOR])
    if lesson["status"] == LessonStatus.CONFIRMED_STUDENT and lesson["studentId"] == session["userId"]:
        abort(403)
    if lesson["status"] == LessonStatus.CONFIRMED_TUTOR and lesson["tutorId"] == session["userId"]:
        abort(403)

    duration = payload.get("duration", "")
    if duration:
        db.update_lesson_duration(lesson["id"], duration)

    if lesson["status"] == LessonStatus.ACCEPTED or duration:
        if lesson["tutorId"] == session["userId"]:
            db.update_lesson_status(lesson["id"], LessonStatus.CONFIRMED_TUTOR)
        else:
            db.update_lesson_status(lesson["id"], LessonStatus.CONFIRMED_STUDENT)
    else:
        tutor_name = db.get_username(lesson["tutorId"])
        message = f"{lesson['actualDurationMinutes']} minutes transferred to {tutor_name}"
        db.add_message(session["room"], -1, -1, datetime.now(), message)

        db.update_lesson_status(lesson["id"], LessonStatus.CONFIRMED)
        db.update_user_balance(lesson["tutorId"], lesson["actualDurationMinutes"])
        if lesson["actualDurationMinutes"] != lesson["proposedDurationMinutes"]:
            difference = lesson["proposedDurationMinutes"] - lesson["actualDurationMinutes"]
            db.update_user_balance(lesson["studentId"], difference)

    _system_message(lesson, LessonStatus.CONFIRMED)
    emit("pageReload", to=session["room"])


@socketio.on("cancelLesson")
def cancel_lesson(payload):
    lesson = db.get_lesson_request(payload["lessonId"])
    _user_lesson_modify(lesson, [LessonStatus.ACCEPTED_STUDENT, LessonStatus.ACCEPTED_TUTOR, LessonStatus.ACCEPTED])

    db.update_lesson_status(lesson["id"], LessonStatus.CANCELLED)
    db.update_user_balance(lesson["studentId"], lesson["proposedDurationMinutes"])
    _system_message(lesson, LessonStatus.CANCELLED)
    emit("pageReload", to=session["room"])


@socketio.on("disconnect")
def handle_disconnect():
    leave_room(session["room"])
