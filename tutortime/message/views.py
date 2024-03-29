from datetime import datetime, timedelta

from flask import Blueprint, abort, render_template, request, session, url_for
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

    contacts, new_msgs = [], []
    rooms = Room.get_by_user(user1.id)
    for room in rooms:
        if len(room.messages) == 0:
            continue
        if room.user1 == user1.id:
            contacts.append(User.get(room.user2))
            new_msgs.append(room.user1_new_messages)
        else:
            contacts.append(User.get(room.user1))
            new_msgs.append(room.user2_new_messages)

    if len(contacts) == 0 and user_id is None:
        return render_template("error/no_contacts.html")

    if user_id:
        user2 = User.get(user_id)
        if user2 is None:
            return render_template("error/nonexistant_user.html")
        if user2 not in contacts:
            contacts.insert(0, user2)
    else:
        user2 = User.get(contacts[0].id)

    room = Room.get_between_users(user1.id, user2.id)
    if room is None:
        room = Room(user1.id, user2.id)
        room.add()
    session["room"] = room.id
    room.read_messages(user1.id)

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
        [lesson for lesson in lessons if lesson.lesson_ts < datetime.now()], key=lambda d: d.lesson_ts, reverse=True
    )
    sorted_lessons += sorted(
        [lesson for lesson in lessons if lesson.lesson_ts >= datetime.now()], key=lambda d: d.lesson_ts, reverse=False
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
        contacts=contacts,
        new_msgs=new_msgs,
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
    user = User.get(session["user_id"])
    peer = User.get(payload["peer_id"])
    timestamp = str_to_dt(f"{payload['date']}T{payload['time']}")
    duration = payload["duration"]
    service = Service.get(payload["service_id"])

    if timestamp < datetime.now() - timedelta(minutes=5):
        return

    if service.user_id == user.id:
        if int(duration) > peer.minutes:
            return

        status = LessonStatus.ACCEPTED_TUTOR
        lesson = Lesson(
            tutor_id=user.id,
            student_id=peer.id,
            service_id=service.id,
            lesson_ts=timestamp,
            proposed_duration=duration,
            actual_duration=duration,
            status=status,
        )
    else:
        if int(duration) > user.minutes:
            return

        status = LessonStatus.ACCEPTED_STUDENT
        lesson = Lesson(
            tutor_id=peer.id,
            student_id=user.id,
            service_id=service.id,
            lesson_ts=timestamp,
            proposed_duration=duration,
            actual_duration=duration,
            status=status,
        )
    lesson.add()

    message = Message(room_id=session["room"], sender_id=user.id, receiver_id=peer.id, lesson_id=lesson.id)
    message.add()
    emit("createLesson", message.to_json(), to=session["room"])


def _user_lesson_modify(lesson: Lesson, accepted_states: list(LessonStatus)):
    if "user_id" not in session:
        abort(401)
    if lesson is None:
        abort(404)
    if session["user_id"] != lesson.tutor_id and session["user_id"] != lesson.student_id:
        abort(403)
    if lesson.status not in accepted_states:
        abort(403)


def _system_message(lesson: Lesson, status: LessonStatus) -> None:
    user = User.get(session["user_id"])
    day = lesson.lesson_ts.strftime("%Y-%m-%d")
    time = lesson.lesson_ts.strftime("%H:%M")
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
    if lesson.proposed_duration > lesson.student.minutes:
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
        lesson.update(lesson.lesson_ts, lesson.proposed_duration, duration)

    _system_message(lesson, LessonStatus.CONFIRMED)

    if lesson.status == LessonStatus.ACCEPTED or duration:
        if lesson.tutor_id == session["user_id"]:
            lesson.update_status(LessonStatus.CONFIRMED_TUTOR)
        else:
            lesson.update_status(LessonStatus.CONFIRMED_STUDENT)
    else:
        lesson.update_status(LessonStatus.CONFIRMED)
        message = f"{lesson.actual_duration} minutes transferred to {lesson.tutor.username}"
        Message(room_id=session["room"], message=message).add()

        minutes_tutored = sum(service.minutes for service in lesson.tutor.services)
        lesson.tutor.update_minutes(lesson.actual_duration)
        lesson.service.update_minutes(lesson.actual_duration)

        if minutes_tutored < 120 and minutes_tutored + lesson.actual_duration >= 120:
            lesson.update_bonus_duration(60)
            lesson.tutor.update_minutes(60)
        if minutes_tutored < 240 and minutes_tutored + lesson.actual_duration >= 240:
            lesson.update_bonus_duration(60)
            lesson.tutor.update_minutes(60)

        if lesson.actual_duration != lesson.proposed_duration:
            lesson.student.update_minutes(lesson.proposed_duration - lesson.actual_duration)

    emit("pageReload", to=session["room"])


@socketio.on("cancelLesson")
def cancel_lesson(payload):
    lesson = Lesson.get(payload["lesson_id"])
    _user_lesson_modify(lesson, [LessonStatus.ACCEPTED_STUDENT, LessonStatus.ACCEPTED_TUTOR, LessonStatus.ACCEPTED])
    if lesson.status == LessonStatus.ACCEPTED:
        lesson.student.update_minutes(lesson.proposed_duration)
    lesson.update_status(LessonStatus.CANCELLED)

    _system_message(lesson, LessonStatus.CANCELLED)
    emit("pageReload", to=session["room"])


@socketio.on("disconnect")
def handle_disconnect():
    if session.get("user_id") and session.get("room") and url_for("message.message_list") in request.referrer:
        Room.get(session["room"]).read_messages(session["user_id"])

    leave_room(session["room"])
