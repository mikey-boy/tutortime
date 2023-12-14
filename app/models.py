import hashlib
import logging
import os
import uuid
from enum import StrEnum, auto
from typing import List, Self

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
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
    services: Mapped[List["Service"]] = relationship()

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

    def update_balance(self, minutes: int):
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
        stmt = select(Service).join(User.services).where(Service.id == service_id)
        return db.session.scalar(stmt)

    def get_services(self, status: ServiceStatus = None):
        if status is None:
            stmt = select(Service).join(User.services)
        else:
            stmt = select(Service).join(User.services).where(Service.status == status)
        return db.session.scalars(stmt)


class Service(Base):
    __tablename__ = "service"

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped["User"] = mapped_column(ForeignKey("user.id"))
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    category: Mapped[str] = mapped_column()
    availability: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column(default=ServiceStatus.ACTIVE)
    minutes: Mapped[int] = mapped_column(default=0)
    images: Mapped[List["Image"]] = relationship("Image")

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


class Image(Base):
    __tablename__ = "image"

    id: Mapped[int] = mapped_column(primary_key=True)
    service: Mapped["Service"] = mapped_column(ForeignKey("service.id"))
    filename: Mapped[str] = mapped_column()
    path: Mapped[str] = mapped_column()

    def __init__(self, service: int, image: FileStorage):
        self.service = service
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
