import calendar
import json
from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from flask import Flask, jsonify, redirect, render_template, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from sassutils.wsgi import SassMiddleware

from database import Database, LessonStatus, ServiceStatus
from image_server import ImageServer
from utils import availability_to_int, availability_to_list

app = Flask(__name__)
app.config.from_object("config")
app.wsgi_app = SassMiddleware(app.wsgi_app, {__name__: ("static/scss", "static/css", "/static/css")})

db = Database(db_folder=app.config["DB_FOLDER"], user_db=app.config["USER_DB"], service_db=app.config["SERVICE_DB"])
image_server = ImageServer(image_folder=app.config["IMAGE_FOLDER"])

socketio = SocketIO(app, logger=True)

if __name__ == "__main__":
    socketio.run(app, debug=True)


@app.route("/")
def root():
    return service_list()


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/user/account/login", methods=["GET", "POST"])
def user_account_login():
    if request.method == "GET":
        if "username" in session:
            return redirect("/user/service/list/active")
        return render_template("user/account/login.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        if username is None or password is None or db.verify_login(username, password) == False:
            if username is None or password is None:
                failure_msg = "Please provide a username and password"
            else:
                failure_msg = "Invalid credentials, try again"
            return render_template("user/account/login.html", failure_msg=failure_msg)
        session["username"] = username
        session["userId"] = db.get_user_id(username)
        return redirect("/service/list/")


@app.route("/user/account/logout")
def user_account_logout():
    if "username" in session:
        del session["username"]
    return redirect("/service/list/")


@app.route("/user/account/create", methods=["GET", "POST"])
def user_account_create():
    if request.method == "GET":
        if "username" in session:
            return render_template("home.html")
        return render_template("user/account/create.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        if username is None or password is None:
            # TODO show error page
            return render_template("failed_user/account/create.html")
        if db.user_exists(username):
            return render_template("user_exists.html")
        user_id = db.add_user(username, password)
        session["username"] = username
        session["userId"] = user_id
        return render_template("home.html")


@app.route("/user/account/list")
def user_account_list():
    if "username" in session:
        services = db.get_services_by_status(session["userId"], ServiceStatus.ACTIVE)
        lessons = db.get_lessons_for_user(session["userId"])
        balance = db.get_user_balance(session["userId"])
        original_balance = balance
        for lesson in lessons:
            dt = datetime.strptime(lesson["datetime"], "%Y-%m-%dT%H:%M")
            lesson["day"] = datetime.strftime(dt, "%d/%m/%Y")
            lesson["tutorName"] = db.get_username(lesson["tutorId"])
            lesson["studentName"] = db.get_username(lesson["studentId"])
            if lesson["tutorId"] == session["userId"] and lesson["status"] == LessonStatus.CONFIRMED:
                lesson["balance"] = balance
                balance -= lesson["actualDurationMinutes"]
            elif lesson["studentId"] == session["userId"] and lesson["status"].startswith("accepted_") == False:
                lesson["balance"] = balance
                balance += lesson["proposedDurationMinutes"]
            else:
                lesson["balance"] = balance

        return render_template(
            "user/account/list.html",
            user_id=session["userId"],
            services=services,
            lessons=lessons,
            balance=original_balance,
        )


@app.route("/service/list/")
@app.route("/service/list/<int:service_id>")
def service_list(service_id=None):
    if service_id:
        service = db.get_service_by_id(service_id)
        images = db.get_images_by_service_id(service_id)
        service["available"] = availability_to_list(service["availability"])
        service["images"] = [
            {"filenameOnServer": image["filenameOnServer"], "filename": image["filename"]} for image in images
        ]
        return render_template("service/display.html", service=service)
    else:
        services = db.get_all_services()
        for service in services:
            images = db.get_images_by_service_id(service["id"])
            service["images"] = [
                {"filenameOnServer": image["filenameOnServer"], "filename": image["filename"]} for image in images
            ]
        return render_template("service/list.html", services=services)


@app.route("/user/service/list/<string:status>")
def user_service_list(status="active"):
    if "username" in session:
        services = db.get_services_by_status(session["userId"], status)
        return render_template("user/service/list.html", services=services, status=status)
    return render_template("user/service/list.html")


@app.route("/user/service/create", methods=["GET", "POST"])
def user_service_create():
    if "username" not in session:
        return render_template("user/account/login.html")
    if request.method == "GET":
        return render_template("user/service/create.html", service={})
    else:
        title = request.form.get("title")
        description = request.form.get("description")
        category = request.form.get("category")
        if title is None or description is None or category is None:
            failure_msg = "Please provide all the required fields"
            return ("user/service/create.html", failure_msg)

        availability = availability_to_int(request.form.keys())
        images = request.files.getlist("images")
        files = image_server.store_images(images)
        db.add_service(session["username"], session["userId"], title, description, category, availability, files)
        return redirect("/user/service/list/active")


@app.route("/user/service/delete/<int:service_id>")
def user_service_delete(service_id):
    result = db.get_service_by_id(service_id)
    if result["username"] == session["username"]:
        images = db.get_images_by_service_id(service_id)
        image_server.remove_images(images)
        db.remove_service(session["username"], service_id)
        return redirect(f'/user/service/list/{result["status"]}')


@app.route("/user/service/update/<int:service_id>", methods=["GET", "POST"])
def user_service_update(service_id):
    if "username" not in session:
        return render_template("user/account/login.html")

    service = db.get_service_by_id(service_id)
    if service["username"] != session["username"]:
        return render_template("home.html")

    if request.method == "GET":
        service["available"] = availability_to_list(service["availability"])
        return render_template("user/service/create.html", service=service)
    else:
        old_images = db.get_images_by_service_id(service_id)
        image_server.remove_images(old_images)

        title = request.form.get("title")
        description = request.form.get("description")
        category = request.form.get("category")
        availability = availability_to_int(request.form.keys())
        images = request.files.getlist("images")
        files = image_server.store_images(images)
        result = db.update_service(session["username"], service_id, title, description, category, availability, files)
        return redirect(f'/user/service/list/{result["status"]}')


@app.route("/user/service/pause/<int:service_id>")
def user_service_pause(service_id):
    if "username" not in session:
        return render_template("user/account/login.html")
    db.pause_service(session["username"], service_id)
    return redirect("/user/service/list/active")


@app.route("/user/service/activate/<int:service_id>")
def user_service_activate(service_id):
    if "username" not in session:
        return render_template("user/account/login.html")
    db.activate_service(session["username"], service_id)
    return redirect("/user/service/list/paused")


@app.route("/user/lesson/confirm/<int:lesson_id>")
def user_lesson_confirm(lesson_id):
    user_id = session["userId"]
    if lesson_id == -1:
        return render_template("home.html")
    db.update_lesson_status(user_id, lesson_id, LessonStatus.CONFIRMED)
    return redirect(request.referrer)


@app.route("/user/lesson/accept/<int:lesson_id>")
def user_lesson_accept(lesson_id):
    user_id = session["userId"]
    if lesson_id == -1:
        return render_template("home.html")
    db.accept_lesson(user_id, lesson_id)
    return redirect(request.referrer)


@app.route("/user/lesson/cancel/<int:lesson_id>")
def user_lesson_cancel(lesson_id):
    user_id = session["userId"]
    if lesson_id == -1:
        return render_template("home.html")
    db.update_lesson_status(user_id, lesson_id, LessonStatus.CANCELLED)
    return redirect(request.referrer)


@app.route("/user/calendar/list")
def user_calendar_list():
    if "username" not in session:
        return render_template("user/calendar/list.html", services=[])

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


@app.route("/user/messages/list/")
@app.route("/user/messages/list/<int:user_id>")
def user_messages_list(user_id=None):
    user1 = {"id": session["userId"], "name": session["username"]}
    user2 = {}

    contacts = db.get_contacts_of_user(user1["id"])

    if user_id:
        user2 = {"id": user_id, "name": db.get_username(user_id)}
    else:
        if contacts == []:
            return render_template("user/messages/list.html", error_text="Browse the service listings to start a chat")
        user2 = {"id": contacts[0]["userId"], "name": contacts[0]["userName"]}

    room = db.get_room_id(user1["id"], user2["id"])
    session["room"] = room

    services = db.get_services_by_status(user1["id"], ServiceStatus.ACTIVE)
    services += db.get_services_by_status(user2["id"], ServiceStatus.ACTIVE)

    upcoming, completed = [], []
    for lesson in db.get_lessons_between_users(user1["id"], user2["id"]):
        dt = datetime.strptime(lesson["datetime"], "%Y-%m-%dT%H:%M")
        lesson["day"] = dt.strftime("%Y-%m-%d")
        lesson["time"] = dt.strftime("%H:%M")
        if dt < datetime.now():
            lesson["completed"] = 1
            lesson["modified"] = True if lesson["proposedDurationMinutes"] != lesson["actualDurationMinutes"] else False
            completed.insert(0, lesson)
        else:
            lesson["completed"] = 0
            upcoming.append(lesson)
    lessons = upcoming + completed

    messages = db.get_messages_between_users(user1["id"], user2["id"])
    for message in messages:
        if message["lessonId"] != -1:
            lesson = db.get_lesson_request(message["lessonId"])
            service = db.get_service_by_id(lesson["serviceId"])

            message["serviceTitle"] = service["title"]
            message["status"] = lesson["status"]
            dt = datetime.strptime(lesson["datetime"], "%Y-%m-%dT%H:%M")
            message["day"] = dt.strftime("%Y-%m-%d")
            message["time"] = dt.strftime("%H:%M")
            message["duration"] = lesson["proposedDurationMinutes"]

    contacts = db.get_contacts_of_user(user1["id"])
    return render_template(
        "user/messages/list.html",
        contacts=contacts,
        user=user1,
        peer=user2,
        services=services,
        lessons=lessons,
        messages=messages,
    )


def _system_message(lesson_id, status):
    user_id = session["userId"]
    username = db.get_username(user_id)
    lesson = db.get_lesson_request(lesson_id)
    service = db.get_service_by_id(lesson["serviceId"])
    dt = datetime.strptime(lesson["datetime"], "%Y-%m-%dT%H:%M")
    day = dt.strftime("%Y-%m-%d")
    time = dt.strftime("%H:%M")
    now = datetime.now().strftime("%Y-%m-%dT%H:%M")
    if status == LessonStatus.ACCEPTED:
        message = f"{username} accepted '{service['title']}' scheduled for {day} @ {time}"
    elif status == LessonStatus.CANCELLED:
        message = f"{username} cancelled '{service['title']}' scheduled for {day} @ {time}"
    else:
        message = (
            f"{username} confirmed '{service['title']}' on {day} @ {time} for {lesson['actualDurationMinutes']} minutes"
        )

    db.add_message(session["room"], -1, -1, now, message)


@socketio.on("connect")
def connect():
    join_room(session["room"])


@socketio.on("message")
def message(payload):
    username = session["username"]
    user_id = session["userId"]
    peer_id = payload["recipient"]
    dt = datetime.now().strftime("%Y-%m-%dT%H:%M")
    payload["message"] = payload["message"].rstrip("\n")

    db.add_message(session["room"], user_id, peer_id, dt, payload["message"])
    message = {"sender": username, "senderId": user_id, "message": payload["message"], "lessonId": -1}
    send(message, to=session["room"])


@socketio.on("createLesson")
def create_lesson(payload):
    username = session["username"]
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
        "sender": username,
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


@socketio.on("modifyLesson")
def modify_lesson(payload):
    username = session["username"]
    user_id = session["userId"]
    peer_id = payload["peerId"]
    lesson_id = payload["lessonId"]
    dt = f"{payload['date']}T{payload['time']}"
    duration = payload["duration"]

    lesson = db.get_lesson_request(lesson_id)
    if lesson["tutorId"] == user_id:
        db.update_lesson(lesson["id"], dt, duration, LessonStatus.ACCEPTED_TUTOR)
    else:
        db.update_lesson(lesson["id"], dt, duration, LessonStatus.ACCEPTED_STUDENT)

    message = db.get_message_by_lesson_id(lesson_id)
    db.update_message(message["id"], user_id, peer_id)
    emit("pageReload", to=session["room"])


@socketio.on("acceptLesson")
def accept_lesson(payload):
    user_id = session["userId"]
    lesson_id = payload["lessonId"]
    db.update_lesson_status(user_id, lesson_id, LessonStatus.ACCEPTED)
    lesson = db.get_lesson_request(lesson_id)
    db.update_user_balance(lesson["studentId"], lesson["proposedDurationMinutes"] * -1)
    _system_message(lesson_id, LessonStatus.ACCEPTED)
    emit("pageReload", to=session["room"])


@socketio.on("confirmLesson")
def confirm_lesson(payload):
    user_id = session["userId"]
    lesson_id = payload["lessonId"]

    duration = payload.get("duration", "")
    if duration:
        db.update_lesson_duration(user_id, lesson_id, duration)

    _system_message(lesson_id, LessonStatus.CONFIRMED)

    lesson = db.get_lesson_request(lesson_id)
    if lesson["status"] == LessonStatus.ACCEPTED or duration:
        if lesson["tutorId"] == user_id:
            db.update_lesson_status(user_id, lesson_id, LessonStatus.CONFIRMED_TUTOR)
        else:
            db.update_lesson_status(user_id, lesson_id, LessonStatus.CONFIRMED_STUDENT)
    else:
        tutor_name = db.get_username(lesson["tutorId"])
        message = f"{lesson['actualDurationMinutes']} minutes transferred to {tutor_name}"
        db.add_message(session["room"], -1, -1, datetime.now(), message)

        db.update_lesson_status(user_id, lesson_id, LessonStatus.CONFIRMED)
        db.update_user_balance(lesson["tutorId"], lesson["actualDurationMinutes"])
        if lesson["actualDurationMinutes"] != lesson["proposedDurationMinutes"]:
            difference = lesson["proposedDurationMinutes"] - lesson["actualDurationMinutes"]
            db.update_user_balance(lesson["studentId"], difference)

    emit("pageReload", to=session["room"])


@socketio.on("cancelLesson")
def cancel_lesson(payload):
    user_id = session["userId"]
    lesson_id = payload["lessonId"]
    db.update_lesson_status(user_id, lesson_id, LessonStatus.CANCELLED)
    lesson = db.get_lesson_request(lesson_id)
    db.update_user_balance(lesson["studentId"], lesson["proposedDurationMinutes"])
    _system_message(lesson_id, LessonStatus.CANCELLED)
    emit("pageReload", to=session["room"])


@socketio.on("disconnect")
def handle_disconnect():
    leave_room(session["room"])
