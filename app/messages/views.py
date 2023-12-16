import datetime
import json
import pickle

from flask import Blueprint, render_template, session
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from models import Lesson, LessonStatus, Message, Room, Service, ServiceStatus, User

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
    messages_json = [message.to_json() for message in room.messages]
    services_json = [service.to_json() for service in services]
    lessons_json = [lesson.to_json() for lesson in lessons]
    return render_template(
        "messages/list.html",
        user=user1,
        peer=user2,
        contacts=user1.get_contacts(),
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

    Message(session["room"], user_id, peer_id, message).add()

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
            tutor=user_id,
            student=peer_id,
            service=service.id,
            timestamp=timestamp,
            proposed_duration=duration,
            actual_duration=duration,
            status=status,
        )
    else:
        status = LessonStatus.ACCEPTED_STUDENT
        lesson = Lesson(
            tutor=peer_id,
            student=user_id,
            service=service.id,
            timestamp=timestamp,
            proposed_duration=duration,
            actual_duration=duration,
            status=status,
        )
    lesson.add()

    message = Message(room=session["room"], sender=user_id, receiver=peer_id, lesson=lesson.id)
    message.add()

    emit("createLesson", message.to_json(), to=session["room"])
