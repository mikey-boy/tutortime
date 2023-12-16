import datetime
import json
import pickle

from flask import Blueprint, abort, render_template, session
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from models import (Lesson, LessonStatus, Message, Room, Service,
                    ServiceStatus, User)

from app import socketio

messages_bp = Blueprint("messages", __name__)


@messages_bp.route("/messages/list/")
@messages_bp.route("/messages/list/<int:user_id>")
def messages_list(user_id=None):
    if session.get("user_id") is None:
        return render_template("error/not_logged_in.html")

    user1 = User.get(session["user_id"])
    if user_id:
        user2 = User.get(user_id)
    else:
        contacts = user1.get_contacts()
        if contacts:
            user2 = User.get(contacts[0].id)
        else:
            return render_template("messages/list.html", error_text="Browse the service listings to start a chat")

    room = Room.get(user1.id, user2.id)
    if room is None:
        room = Room(user1.id, user2.id)
        room.add()
    session["room"] = room.id

    lessons = []
    for service in user1.services:
        lessons += service.get_lessons_with_user(user2.id)
    for service in user2.services:
        lessons += service.get_lessons_with_user(user1.id)
    services = user1.get_services(ServiceStatus.ACTIVE) + user2.get_services(ServiceStatus.ACTIVE)

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    contacts_json = [contact.to_json() for contact in user1.get_contacts()]
    messages_json = [message.to_json() for message in room.messages]
    services_json = [service.to_json() for service in services]
    lessons_json = [lesson.to_json() for lesson in lessons]
    return render_template(
        "messages/list.html",
        user=user1.to_json(),
        peer=user2.to_json(),
        contacts=contacts_json,
        messages=messages_json,
        services=services_json,
        lessons=lessons_json,
        today=today,
    )


@socketio.on("connect")
def connect():
    join_room(session["room"])


@socketio.on("message")
def message(payload):
    user_id = session["user_id"]
    peer_id = payload["peer_id"]
    message = payload["message"].rstrip("\n")

    Message(room_id=session["room"], sender=user_id, receiver=peer_id, message=message).add()

    json_message = {"sender": user_id, "message": payload["message"]}
    send(json_message, to=session["room"])


@socketio.on("createLesson")
def create_lesson(payload):
    user_id = session["user_id"]
    peer_id = payload["peer_id"]

    timestamp = datetime.datetime.strptime(f"{payload['date']}T{payload['time']}", "%Y-%m-%dT%H:%M")
    duration = payload["duration"]
    service = Service.get(payload["service_id"])

    if service.user == user_id:
        status = LessonStatus.ACCEPTED_TUTOR
        lesson = Lesson(
            tutor_id=user_id,
            student_id=peer_id,
            service_id=service.id,
            timestamp=timestamp,
            proposed_duration=duration,
            actual_duration=duration,
            status=status,
        )
    else:
        status = LessonStatus.ACCEPTED_STUDENT
        lesson = Lesson(
            tutor_id=peer_id,
            student_id=user_id,
            service_id=service.id,
            timestamp=timestamp,
            proposed_duration=duration,
            actual_duration=duration,
            status=status,
        )
    lesson.add()

    message = Message(room_id=session["room"], sender=user_id, receiver=peer_id, lesson_id=lesson.id)
    message.add()

    emit("createLesson", message.to_json(), to=session["room"])

def _user_lesson_modify(lesson: Lesson, accepted_states: list(LessonStatus)):
    if "user_id" not in session:
        abort(401)
    if session["user_id"] != lesson.tutor_id and session["user_id"] != lesson.student_id:
        abort(403)
    if lesson.status not in accepted_states:
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
    lesson = Lesson.get(payload["lesson_id"])
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
