from datetime import datetime

from flask import Blueprint, abort, render_template, session
from flask_socketio import emit, join_room, leave_room, send

from tutortime.extensions import socketio
from tutortime.models import Lesson, LessonStatus, Message, Room, Service, ServiceStatus, User
from tutortime.utils import str_to_dt

message_bp = Blueprint("message", __name__)


@message_bp.route("/message/list/")
@message_bp.route("/message/list/<int:user_id>")
def message_list(user_id=None):
    if session.get("user_id") is None:
        return render_template("error/not_logged_in.html", action="talk to other users on the platform")

    user1 = User.get(session["user_id"])
    if user_id:
        user2 = User.get(user_id)
    else:
        contacts = user1.get_contacts()
        if contacts:
            user2 = User.get(contacts[0].id)
        else:
            return render_template("error/no_contacts.html")

    room = Room.get(user1.id, user2.id)
    if room is None:
        room = Room(user1.id, user2.id)
        room.add()
    session["room"] = room.id

    lessons = []
    statuses = [
        LessonStatus.ACCEPTED,
        LessonStatus.CONFIRMED,
        LessonStatus.CONFIRMED_STUDENT,
        LessonStatus.CONFIRMED_TUTOR,
    ]
    for service in user1.services:
        lessons += service.get_lessons(user2.id, statuses)
    for service in user2.services:
        lessons += service.get_lessons(user1.id, statuses)
    sorted_lessons = sorted(
        [lesson for lesson in lessons if lesson.timestamp < datetime.now()], key=lambda d: d.timestamp, reverse=True
    )
    sorted_lessons += sorted(
        [lesson for lesson in lessons if lesson.timestamp >= datetime.now()], key=lambda d: d.timestamp, reverse=False
    )

    services = user1.get_services(ServiceStatus.ACTIVE) + user2.get_services(ServiceStatus.ACTIVE)

    today = datetime.now().strftime("%Y-%m-%d")
    messages_json = [message.to_json() for message in room.messages]
    services_json = [service.to_json() for service in services]
    lessons_json = [lesson.to_json() for lesson in sorted_lessons]
    return render_template(
        "message/list.html",
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

    message = Message(room_id=session["room"], sender_id=user_id, receiver_id=peer_id, message=message)
    message.add()
    send(message.to_json(), to=session["room"])


@socketio.on("createLesson")
def create_lesson(payload):
    user_id = session["user_id"]
    peer_id = payload["peer_id"]

    timestamp = str_to_dt(f"{payload['date']}T{payload['time']}")
    duration = payload["duration"]
    service = Service.get(payload["service_id"])

    if service.user_id == user_id:
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

    message = Message(room_id=session["room"], sender_id=user_id, receiver_id=peer_id, lesson_id=lesson.id)
    message.add()
    emit("createLesson", message.to_json(), to=session["room"])


def _user_lesson_modify(lesson: Lesson, accepted_states: list(LessonStatus)):
    if "user_id" not in session:
        abort(401)
    if session["user_id"] != lesson.tutor_id and session["user_id"] != lesson.student_id:
        abort(403)
    if lesson.status not in accepted_states:
        abort(403)


def _system_message(lesson: Lesson, status: LessonStatus) -> None:
    user = User.get(session["user_id"])
    day = lesson.timestamp.strftime("%Y-%m-%d")
    time = lesson.timestamp.strftime("%H:%M")
    if status == LessonStatus.ACCEPTED:
        message = f"{user.username} accepted '{lesson.service.title}' scheduled for {day} @ {time}"
    elif status == LessonStatus.CANCELLED:
        message = f"{user.username} cancelled '{lesson.service.title}' scheduled for {day} @ {time}"
    else:
        message = (
            f"{user.username} confirmed '{lesson.service.title}' on {day} @ {time} for {lesson.actual_duration} minutes"
        )

    Message(room_id=session["room"], message=message).add()


@socketio.on("modifyLesson")
def modify_lesson(payload):
    lesson = Lesson.get(payload["lesson_id"])
    _user_lesson_modify(lesson, [LessonStatus.ACCEPTED_STUDENT, LessonStatus.ACCEPTED_TUTOR])

    timestamp = str_to_dt(f"{payload['date']}T{payload['time']}")
    duration = payload["duration"]
    lesson.update(timestamp, duration, duration)

    if lesson.tutor_id == session["user_id"]:
        lesson.update_status(LessonStatus.ACCEPTED_TUTOR)
    else:
        lesson.update_status(LessonStatus.ACCEPTED_STUDENT)

    if lesson.message.sender_id != session["user_id"]:
        lesson.message.swap_sender()
    emit("pageReload", to=session["room"])


@socketio.on("acceptLesson")
def accept_lesson(payload):
    lesson = Lesson.get(payload["lesson_id"])
    _user_lesson_modify(lesson, [LessonStatus.ACCEPTED_STUDENT, LessonStatus.ACCEPTED_TUTOR])

    if lesson.status == LessonStatus.ACCEPTED_STUDENT and lesson.student_id == session["user_id"]:
        abort(403)
    if lesson.status == LessonStatus.ACCEPTED_TUTOR and lesson.tutor_id == session["user_id"]:
        abort(403)

    lesson.update_status(LessonStatus.ACCEPTED)
    lesson.student.update_minutes(lesson.proposed_duration * -1)
    _system_message(lesson, LessonStatus.ACCEPTED)
    emit("pageReload", to=session["room"])


@socketio.on("confirmLesson")
def confirm_lesson(payload):
    lesson = Lesson.get(payload["lesson_id"])
    _user_lesson_modify(lesson, [LessonStatus.ACCEPTED, LessonStatus.CONFIRMED_STUDENT, LessonStatus.CONFIRMED_TUTOR])
    if lesson.status == LessonStatus.CONFIRMED_STUDENT and lesson.student_id == session["user_id"]:
        abort(403)
    if lesson.status == LessonStatus.CONFIRMED_TUTOR and lesson.tutor_id == session["user_id"]:
        abort(403)

    duration = payload.get("duration", "")
    if duration:
        lesson.update(lesson.timestamp, lesson.proposed_duration, duration)

    _system_message(lesson, LessonStatus.CONFIRMED)

    if lesson.status == LessonStatus.ACCEPTED or duration:
        if lesson.tutor_id == session["user_id"]:
            lesson.update_status(LessonStatus.CONFIRMED_TUTOR)
        else:
            lesson.update_status(LessonStatus.CONFIRMED_STUDENT)
    else:
        message = f"{lesson.actual_duration} minutes transferred to {lesson.tutor.username}"
        Message(room_id=session["room"], message=message).add()

        lesson.update_status(LessonStatus.CONFIRMED)
        lesson.tutor.update_minutes(lesson.actual_duration)
        if lesson.actual_duration != lesson.proposed_duration:
            lesson.student.update_minutes(lesson.proposed_duration - lesson.actual_duration)

    emit("pageReload", to=session["room"])


@socketio.on("cancelLesson")
def cancel_lesson(payload):
    lesson = Lesson.get(payload["lesson_id"])
    _user_lesson_modify(lesson, [LessonStatus.ACCEPTED_STUDENT, LessonStatus.ACCEPTED_TUTOR, LessonStatus.ACCEPTED])

    lesson.update_status(LessonStatus.CANCELLED)
    lesson.student.update_minutes(lesson.proposed_duration)
    _system_message(lesson, LessonStatus.CANCELLED)
    emit("pageReload", to=session["room"])


@socketio.on("disconnect")
def handle_disconnect():
    leave_room(session["room"])
