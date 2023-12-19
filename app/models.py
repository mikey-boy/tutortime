import hashlib
import logging
import os
import uuid
from datetime import datetime
from enum import StrEnum, auto
from typing import List, Optional, Self

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from werkzeug.datastructures import FileStorage

from app import app


class Base(DeclarativeBase):
    pass


class ServiceStatus(StrEnum):
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


db = SQLAlchemy(model_class=Base)
db.init_app(app)


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
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

    def update_minutes(self, minutes: int) -> None:
        self.minutes += minutes
        db.session.commit()

    def get(id: int) -> Self:
        stmt = select(User).where(User.id == id)
        return db.session.scalar(stmt)

    def get_by_creds(username: str, password: str) -> Self | None:
        stmt = select(User).where(User.username == username)
        user = db.session.scalar(stmt)
        if user.password == hashlib.sha256(password.encode()).hexdigest():
            return user
        return None

    def get_service(self, service_id: int):
        for service in self.services:
            if service.id == service_id:
                return service

    def get_services(self, status: ServiceStatus = None):
        if status:
            return [service for service in self.services if service.status == status]
        return self.services

    def get_contacts(self):
        stmt = select(Room).where((Room.user1 == self.id) | (Room.user2 == self.id))
        rooms = db.session.scalars(stmt)
        users = []
        for room in rooms:
            if room.user1 == self.id:
                users.append(User.get(room.user2))
            else:
                users.append(User.get(room.user1))
        return users


class Service(Base):
    __tablename__ = "service"

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped["User"] = relationship(back_populates="services")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    category: Mapped[ServiceCategory] = mapped_column()
    status: Mapped[ServiceStatus] = mapped_column(default=ServiceStatus.ACTIVE)
    availability: Mapped[int] = mapped_column()
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
        db.session.delete(self)
        db.session.commit()

    def update(self, title: str, description: str, category: str, availability: int) -> None:
        self.title = title
        self.description = description
        self.category = category
        self.availability = availability
        db.session.commit()

    def update_status(self, status: ServiceStatus) -> None:
        self.status = status
        db.session.commit()

    def get(id: int) -> Self:
        stmt = select(Service).where(Service.id == id)
        return db.session.scalar(stmt)

    def get_all_services(category: ServiceCategory = None):
        if category is None:
            stmt = select(Service)
        else:
            stmt = select(Service).where(Service.category == category)
        return db.session.scalars(stmt)

    def get_lessons(self, student_id: int, statuses: list(LessonStatus)):
        return [lesson for lesson in self.lessons if lesson.student_id == student_id and lesson.status in statuses]


class Image(Base):
    __tablename__ = "image"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("service.id"))
    service: Mapped["Service"] = relationship(back_populates="images")
    filename: Mapped[str] = mapped_column()
    path: Mapped[str] = mapped_column()

    def __init__(self, service_id: int, image: FileStorage):
        self.service_id = service_id
        self.filename = image.filename
        self.path = os.path.join(app.config["IMAGE_FOLDER"], str(uuid.uuid4()))

        image.save(self.path)

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


class Lesson(Base):
    __tablename__ = "lesson"

    id: Mapped[int] = mapped_column(primary_key=True)
    tutor_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    tutor: Mapped["User"] = relationship(foreign_keys=tutor_id)
    student_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    student: Mapped["User"] = relationship(foreign_keys=student_id)
    service_id: Mapped[int] = mapped_column(ForeignKey("service.id"))
    service: Mapped["Service"] = relationship(back_populates="lessons")
    timestamp: Mapped[datetime] = mapped_column()
    proposed_duration: Mapped[int] = mapped_column()
    actual_duration: Mapped[int] = mapped_column()
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
            "day": self.timestamp.strftime("%Y-%m-%d"),
            "time": self.timestamp.strftime("%H:%M"),
            "proposed_duration": self.proposed_duration,
            "actual_duration": self.actual_duration,
            "modified": self.proposed_duration != self.actual_duration,
            "service_id": self.service.id,
            "completed": self.timestamp < datetime.now(),
        }
        return data

    def add(self) -> None:
        db.session.add(self)
        db.session.commit()

    def get(id: int) -> Self:
        stmt = select(Lesson).where(Lesson.id == id)
        return db.session.scalar(stmt)

    def get_lessons_for_user(user_id: int, statuses: list(LessonStatus), asc: bool = True):
        stmt = (
            select(Lesson)
            .where((Lesson.student_id == user_id) | (Lesson.tutor_id == user_id))
            .where(Lesson.status.in_(statuses))
        )
        if asc:
            stmt = stmt.order_by(Lesson.timestamp)
        else:
            stmt = stmt.order_by(desc(Lesson.timestamp))
        return db.session.scalars(stmt)

    def update(self, timestamp: datetime, proposed_duration: int, actual_duration: int):
        self.timestamp = timestamp
        self.proposed_duration = proposed_duration
        self.actual_duration = actual_duration
        db.session.commit()

    def update_status(self, status: LessonStatus) -> None:
        self.status = status
        db.session.commit()


class Room(Base):
    __tablename__ = "room"

    id: Mapped[int] = mapped_column(primary_key=True)
    user1: Mapped[int] = mapped_column()
    user2: Mapped[int] = mapped_column()
    messages: Mapped[List["Message"]] = relationship(back_populates="room")

    def __init__(self, user1: int, user2: int):
        self.user1 = min(user1, user2)
        self.user2 = max(user1, user2)

    def add(self) -> None:
        db.session.add(self)
        db.session.commit()

    def get(user1: int, user2: int) -> Self | None:
        if user1 > user2:
            user1, user2 = user2, user1
        stmt = select(Room).where(Room.user1 == user1).where(Room.user2 == user2)
        return db.session.scalar(stmt)


class Message(Base):
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
        db.session.commit()

    def swap_sender(self) -> None:
        self.sender_id, self.receiver_id = self.receiver_id, self.sender_id
        db.session.commit()
