import hashlib
import logging
import os
import uuid
from datetime import datetime, timedelta
from enum import StrEnum, auto
from typing import List, Optional, Self

from flask import current_app
from sqlalchemy import ForeignKey, desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from werkzeug.datastructures import FileStorage

from tutortime.extensions import db, scheduler


class ServiceStatus(StrEnum):
    CANCELLED = auto()
    ACTIVE = auto()
    PAUSED = auto()


class ServiceCategory(StrEnum):
    LANGUAGE = auto()
    MUSIC = auto()
    SOFTWARE = auto()
    WELLNESS = auto()
    OTHER = auto()


class LessonStatus(StrEnum):
    CANCELLED = auto()
    EXPIRED = auto()
    ACCEPTED = auto()
    ACCEPTED_STUDENT = auto()
    ACCEPTED_TUTOR = auto()
    CONFIRMED = auto()
    CONFIRMED_STUDENT = auto()
    CONFIRMED_TUTOR = auto()


DEFAULT_PROFILE_IMG = "/static/img/default/tux.png"
DEFAULT_SERVICE_IMG = {
    ServiceCategory.LANGUAGE: "/static/img/default/language.jpg",
    ServiceCategory.SOFTWARE: "/static/img/default/software.jpg",
    ServiceCategory.WELLNESS: "/static/img/default/wellness.jpg",
    ServiceCategory.MUSIC: "/static/img/default/music.jpg",
    ServiceCategory.OTHER: "/static/img/default/other.jpg",
}


class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    social_id: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    availability: Mapped[int] = mapped_column(default=0)
    image_path: Mapped[str] = mapped_column(default=DEFAULT_PROFILE_IMG)
    timezone: Mapped[int] = mapped_column()
    minutes: Mapped[int] = mapped_column(default=60)
    services: Mapped[List["Service"]] = relationship(back_populates="user")

    def add(self) -> bool:
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            return False

    def remove(self) -> None:
        db.session.delete(self)
        db.session.commit()

    def update(self, username: str, description: str, availability: str, image: FileStorage = None) -> None:
        self.username = username
        self.description = description
        self.availability = availability

        if image:
            if self.image_path and self.image_path != DEFAULT_PROFILE_IMG:
                try:
                    os.remove(self.image_path)
                except FileNotFoundError:
                    logging.warning(f"Image not found on server: '{self.image_path}'")

            self.image_path = os.path.join(current_app.config["IMAGE_FOLDER"], str(uuid.uuid4()))
            image.save(self.image_path[1:])

        db.session.commit()

    def update_minutes(self, minutes: int) -> None:
        self.minutes += minutes
        db.session.commit()

    def username_exists(username: str) -> bool:
        stmt = select(User).where(User.username == username)
        user = db.session.scalar(stmt)
        return user is not None

    def get(id: int) -> Optional[Self]:
        stmt = select(User).where(User.id == id)
        return db.session.scalar(stmt)

    def get_by_creds(username: str, password: str) -> Optional[Self]:
        stmt = select(User).where(User.username == username)
        user = db.session.scalar(stmt)
        if user is not None and user.password == hashlib.sha256(password.encode()).hexdigest():
            return user
        return None

    def get_by_social_id(social_id: str) -> Optional[Self]:
        stmt = select(User).where(User.social_id == social_id)
        user = db.session.scalar(stmt)
        return user

    def get_service(self, service_id: int):
        for service in self.services:
            if service.id == service_id:
                return service

    def get_services(self, status: ServiceStatus = None):
        if status:
            return [service for service in self.services if service.status == status]
        return self.services


class Service(db.Model):
    __tablename__ = "service"

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped["User"] = relationship(back_populates="services")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    category: Mapped[ServiceCategory] = mapped_column()
    status: Mapped[ServiceStatus] = mapped_column(default=ServiceStatus.ACTIVE)
    minutes: Mapped[int] = mapped_column(default=0)
    images: Mapped[List["Image"]] = relationship(back_populates="service")
    lessons: Mapped[List["Lesson"]] = relationship(back_populates="service")

    def to_json(self) -> dict:
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
        }
        return data

    def add(self) -> None:
        db.session.add(self)
        db.session.commit()

    def remove(self) -> None:
        for image in self.images:
            image.remove()
        self.update(LessonStatus.CANCELLED)

    def update(self, title: str, description: str, category: str, availability: int) -> None:
        self.title = title
        self.description = description
        self.category = category
        db.session.commit()

    def update_status(self, status: ServiceStatus) -> None:
        self.status = status
        db.session.commit()

    def update_minutes(self, minutes: int) -> None:
        self.minutes += minutes
        db.session.commit()

    def get(id: int) -> Self:
        stmt = select(Service).where(Service.id == id)
        return db.session.scalar(stmt)

    def get_page(search: str = "", category: ServiceCategory = "", page_num: int = 1, per_page: int = 20):
        stmt = select(Service).where(Service.status == ServiceStatus.ACTIVE)
        if category:
            stmt = stmt.where(Service.category == category)
        if search != "":
            search = f"%{search}%"
            stmt = stmt.filter((Service.title.like(search)) | Service.description.like(search))

        stmt = stmt.order_by(Service.id.desc())
        return db.paginate(stmt, page=page_num, per_page=per_page, error_out=False)

    def get_lessons(self, student_id: int, statuses: list(LessonStatus)):
        return [lesson for lesson in self.lessons if lesson.student_id == student_id and lesson.status in statuses]


class Image(db.Model):
    __tablename__ = "image"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("service.id"))
    service: Mapped["Service"] = relationship(back_populates="images")
    filename: Mapped[str] = mapped_column()
    path: Mapped[str] = mapped_column()

    def __init__(self, service_id: int, image: FileStorage = None, category: ServiceCategory = None) -> None:
        self.service_id = service_id

        if image:
            self.filename = image.filename
            self.path = os.path.join(current_app.config["IMAGE_FOLDER"], str(uuid.uuid4()))
            image.save(self.path[1:])
        else:
            self.filename = DEFAULT_SERVICE_IMG[category]
            self.path = DEFAULT_SERVICE_IMG[category]

    def add(self) -> None:
        db.session.add(self)
        db.session.commit()

    def remove(self) -> None:
        try:
            os.remove(self.path)
        except FileNotFoundError:
            logging.warning(f"Image not found on server: '{self.path}'")

        db.session.delete(self)
        db.session.commit()


class Lesson(db.Model):
    __tablename__ = "lesson"

    id: Mapped[int] = mapped_column(primary_key=True)
    creation_ts: Mapped[datetime] = mapped_column(server_default=func.now())
    tutor_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    tutor: Mapped["User"] = relationship(foreign_keys=tutor_id)
    student_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    student: Mapped["User"] = relationship(foreign_keys=student_id)
    service_id: Mapped[int] = mapped_column(ForeignKey("service.id"))
    service: Mapped["Service"] = relationship(back_populates="lessons")
    lesson_ts: Mapped[datetime] = mapped_column()
    proposed_duration: Mapped[int] = mapped_column()
    actual_duration: Mapped[int] = mapped_column()
    bonus_duration: Mapped[int] = mapped_column(default=0)
    status: Mapped[LessonStatus] = mapped_column()
    message: Mapped["Message"] = relationship(back_populates="lesson")

    def to_json(self) -> dict:
        data = {
            "id": self.id,
            "title": self.service.title,
            "description": self.service.description,
            "tutor_id": self.tutor_id,
            "tutor_name": self.tutor.username,
            "student_id": self.student_id,
            "student_name": self.student.username,
            "status": self.status,
            "day": self.lesson_ts.strftime("%Y-%m-%d"),
            "time": self.lesson_ts.strftime("%H:%M"),
            "proposed_duration": self.proposed_duration,
            "actual_duration": self.actual_duration,
            "bonus_duration": self.bonus_duration,
            "modified": self.proposed_duration != self.actual_duration,
            "service_id": self.service.id,
            "completed": self.lesson_ts < datetime.now(),
        }
        return data

    def add(self) -> None:
        db.session.add(self)
        db.session.commit()

    def get(id: int) -> Optional[Self]:
        stmt = select(Lesson).where(Lesson.id == id)
        return db.session.scalar(stmt)

    def get_lessons_for_user(user_id: int, statuses: list(LessonStatus), asc: bool = True):
        stmt = (
            select(Lesson)
            .where((Lesson.student_id == user_id) | (Lesson.tutor_id == user_id))
            .where(Lesson.status.in_(statuses))
        )
        if asc:
            stmt = stmt.order_by(Lesson.lesson_ts)
        else:
            stmt = stmt.order_by(desc(Lesson.lesson_ts))
        return db.session.scalars(stmt)

    def update(self, timestamp: datetime, proposed_duration: int, actual_duration: int) -> None:
        self.lesson_ts = timestamp
        self.proposed_duration = proposed_duration
        self.actual_duration = actual_duration
        db.session.commit()

    def update_status(self, status: LessonStatus) -> None:
        self.status = status
        db.session.commit()

    def update_bonus_duration(self, bonus_duration: int) -> None:
        self.bonus_duration += bonus_duration
        db.session.commit()

    # DB Maintenance
    @scheduler.task("interval", id="expire_lessons", seconds=10, misfire_grace_time=900)
    def expire_lessons():
        with scheduler.app.app_context():
            # Lessons that are scheduled at least two days in advance and start within 24 hours
            stmt = (
                select(Lesson)
                .where(func.extract("epoch", Lesson.lesson_ts - Lesson.creation_ts) > timedelta(days=2).total_seconds())
                .where(func.extract("epoch", Lesson.lesson_ts - datetime.now()) < timedelta(days=1).total_seconds())
                .where(Lesson.status.in_([LessonStatus.ACCEPTED_STUDENT, LessonStatus.ACCEPTED_TUTOR]))
            )
            # Lessons that are scheduled less than two days in advance and are not accepted before their start date
            stmt2 = (
                select(Lesson)
                .where(Lesson.lesson_ts < datetime.now() - timedelta(minutes=10))
                .where(Lesson.status.in_([LessonStatus.ACCEPTED_STUDENT, LessonStatus.ACCEPTED_TUTOR]))
            )

            lessons = db.session.scalars(stmt)
            lessons2 = db.session.scalars(stmt2)
            for lesson in lessons:
                lesson.update_status(LessonStatus.EXPIRED)
            for lesson in lessons2:
                lesson.update_status(LessonStatus.EXPIRED)


class Room(db.Model):
    __tablename__ = "room"

    id: Mapped[int] = mapped_column(primary_key=True)
    user1: Mapped[int] = mapped_column()
    user2: Mapped[int] = mapped_column()
    user1_new_messages: Mapped[bool] = mapped_column(default=False)
    user2_new_messages: Mapped[bool] = mapped_column(default=False)
    messages: Mapped[List["Message"]] = relationship(back_populates="room")

    def __init__(self, user1: int, user2: int) -> None:
        self.user1 = min(user1, user2)
        self.user2 = max(user1, user2)

    def add(self) -> None:
        db.session.add(self)
        db.session.commit()

    def read_messages(self, user_id: int) -> None:
        if user_id == self.user1:
            self.user1_new_messages = False
        else:
            self.user2_new_messages = False
        db.session.commit()

    def get(id: int) -> Optional[Self]:
        stmt = select(Room).where(Room.id == id)
        return db.session.scalar(stmt)

    def get_between_users(user1: int, user2: int) -> Optional[Self]:
        if user1 > user2:
            user1, user2 = user2, user1
        stmt = select(Room).where(Room.user1 == user1).where(Room.user2 == user2)
        return db.session.scalar(stmt)

    def get_by_user(user_id: int):
        stmt = select(Room).where((Room.user1 == user_id) | (Room.user2 == user_id))
        rooms = list(db.session.scalars(stmt))

        def get_latest_message_timestamp(room: Self):
            if room.messages:
                return room.messages[-1].timestamp.timestamp()
            else:
                return 0

        rooms.sort(key=get_latest_message_timestamp, reverse=True)
        return rooms


class Message(db.Model):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("room.id"))
    room: Mapped["Room"] = relationship(back_populates="messages")
    sender_id: Mapped[Optional[int]] = mapped_column()
    receiver_id: Mapped[Optional[int]] = mapped_column()
    message: Mapped[Optional[str]] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column(server_default=func.now())
    lesson_id: Mapped[Optional[int]] = mapped_column(ForeignKey("lesson.id"))
    lesson: Mapped[Optional["Lesson"]] = relationship(back_populates="message")

    def to_json(self) -> dict:
        data = {"sender": self.sender_id, "receiver": self.receiver_id, "message": self.message}
        if self.lesson:
            data["lesson"] = self.lesson.to_json()
        return data

    def add(self) -> None:
        db.session.add(self)

        room = Room.get(self.room_id)
        if room.user1 == self.sender_id:
            room.user2_new_messages = True
        else:
            room.user1_new_messages = True

        db.session.commit()

    def swap_sender(self) -> None:
        self.sender_id, self.receiver_id = self.receiver_id, self.sender_id
        db.session.commit()
