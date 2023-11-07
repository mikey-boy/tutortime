import hashlib
import os
import sqlite3
from enum import StrEnum, auto


def _crud(db: str, query: str):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()


class BookingStatus(StrEnum):
    PENDING = auto()
    CONFIRMED = auto()
    CANCELLED = auto()


class ServiceStatus(StrEnum):
    ACTIVE = auto()
    PAUSED = auto()


class ServiceCategory(StrEnum):
    LANGUAGE = auto()
    MUSIC = auto()
    SOFTWARE = auto()
    WELLNESS = auto()
    OTHER = auto()


class Database:
    def __init__(self, db_folder: str, user_db: str, service_db: str):
        os.makedirs(db_folder, exist_ok=True)

        self.service_db = os.path.join(db_folder, service_db)
        self.user_db = os.path.join(db_folder, user_db)

        user_schema = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT
            )
        """
        message_schema = """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                roomId INTEGER,
                senderId INTEGER,
                recipientId INTEGER,
                datetime INTEGER,
                message TEXT,
                bookingId INTEGER
            )
        """
        room_schema = """
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY,
                userId INTEGER,
                peerId INTEGER,
                userName TEXT,
                peerName TEXT
            )
        """
        service_schema = """
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY,
                userId INTEGER,
                username TEXT,
                title TEXT, 
                description TEXT,
                category TEXT,
                availability INTEGER,
                status TEXT,
                totalMinutes INTEGER
            )
        """
        booking_schema = """
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY,
                serviceId INTEGER,
                tutorId INTEGER,
                studentId INTEGER,
                status TEXT,
                datetime TEXT,
                durationMinutes INTEGER
            )
        """
        image_schema = """
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY,
                serviceId INTEGER,
                filename TEXT,
                filenameOnServer TEXT
            )
        """

        _crud(self.user_db, user_schema)
        _crud(self.user_db, message_schema)
        _crud(self.user_db, room_schema)
        _crud(self.user_db, service_schema)
        _crud(self.user_db, image_schema)
        _crud(self.user_db, booking_schema)

    def user_exists(self, username: str):
        conn = sqlite3.connect(self.user_db)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def get_user_id(self, username: str):
        conn = sqlite3.connect(self.user_db)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        return -1

    def get_username(self, user_id: int):
        conn = sqlite3.connect(self.user_db)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        return ""

    def verify_login(self, username: str, password: str):
        conn = sqlite3.connect(self.user_db)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        if result is None:
            return False
        return result[0] == hashlib.sha256(password.encode()).hexdigest()

    def add_user(self, username: str, password: str):
        if self.user_exists(username) == False:
            conn = sqlite3.connect(self.user_db)
            cursor = conn.cursor()
            encoded_pass = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute("INSERT INTO users (username, password) VALUES(?, ?)", (username, encoded_pass))
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id

    def remove_user(self, username: str):
        if self.user_exists(username):
            conn = sqlite3.connect(self.user_db)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
            conn.close()

    def add_room(self, user_id, peer_id):
        conn = sqlite3.connect(self.user_db)
        cursor = conn.cursor()
        user_name = self.get_username(user_id)
        peer_name = self.get_username(peer_id)
        sql = "INSERT INTO rooms (userId, peerId, userName, peerName) VALUES(?, ?, ?, ?)"
        cursor.execute(sql, (user_id, peer_id, user_name, peer_name))
        room_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return room_id

    def get_room_id(self, user1: int, user2: int):
        user_id, peer_id = user1, user2
        if user1 < user2:
            user_id, peer_id = user2, user1
        conn = sqlite3.connect(self.user_db)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM rooms WHERE userId = ? AND peerId = ?", (user_id, peer_id))
        results = cursor.fetchone()
        conn.close()
        if results is None:
            return self.add_room(user_id, peer_id)
        return results[0]

    def get_contacts_of_user(self, user_id: int):
        conn = sqlite3.connect(self.user_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        sql = """
        SELECT userId, userName FROM rooms WHERE peerId = ? UNION
        SELECT peerId, peerName FROM rooms WHERE userId = ?
        """
        cursor.execute(sql, (user_id, user_id))
        results = cursor.fetchall()
        conn.close()
        return [dict(result) for result in results]

    def add_message(
        self, room_id: int, sender_id: int, recipient_id: int, datetime: str, message: str, booking_id: int = -1
    ):
        conn = sqlite3.connect(self.user_db)
        cursor = conn.cursor()
        sql = "INSERT INTO messages (roomId, senderId, recipientId, datetime, message, bookingId) VALUES(?, ?, ?, ?, ?, ?)"
        cursor.execute(sql, (room_id, sender_id, recipient_id, datetime, message, booking_id))
        conn.commit()
        conn.close()

    def get_messages_between_users(self, user1: int, user2: int):
        room_id = self.get_room_id(user1, user2)
        conn = sqlite3.connect(self.user_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        sql = """
        SELECT
            senderId, recipientId, message, bookingId, serviceId, bookings.datetime, bookings.durationMinutes, bookings.status
        FROM
            messages
        LEFT JOIN
            bookings
        ON
            messages.bookingId = bookings.id
        WHERE 
            roomId = ?
        """
        cursor.execute(sql, (room_id,))
        results = cursor.fetchall()
        conn.close()
        return [dict(result) for result in results]

    def get_booking_request(self, booking_id):
        conn = sqlite3.connect(self.user_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT senderId, recipientId FROM messages WHERE bookingId = ?", (booking_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result)

    def get_images_by_service_id(self, id: str):
        conn = sqlite3.connect(self.user_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT filename, filenameOnServer FROM images WHERE serviceId = ?", (id,))
        results = cursor.fetchall()
        conn.close()
        return [dict(result) for result in results]

    def add_service(
        self, username: str, user_id: int, title: str, description: str, category: str, availability: int, images: list
    ):
        if category in iter(ServiceCategory):
            conn = sqlite3.connect(self.user_db)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO services (username, userId, title, description, category, availability, status, totalMinutes) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                (username, user_id, title, description, category, availability, ServiceStatus.ACTIVE, 0),
            )
            service_id = cursor.lastrowid
            for image in images:
                cursor.execute(
                    "INSERT INTO images (serviceId, filename, filenameOnServer) VALUES (?, ?, ?)",
                    (service_id, image["filename"], image["filenameOnServer"]),
                )
            conn.commit()
            conn.close()

    def get_services_by_status(self, user_id: str, status: str):
        if status in iter(ServiceStatus):
            conn = sqlite3.connect(self.user_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, description FROM services WHERE userId = ? AND status = ?", (user_id, status)
            )
            results = cursor.fetchall()
            conn.close()
            return [dict(result) for result in results]

    def get_service_by_id(self, service_id: int):
        conn = sqlite3.connect(self.user_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, userId, title, description, category, availability, status, username FROM services WHERE id = ?",
            (service_id,),
        )
        result = cursor.fetchone()
        conn.close()
        return dict(result)

    def get_images_by_service_id(self, service_id: int):
        conn = sqlite3.connect(self.user_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT filename, filenameOnServer FROM images WHERE serviceId = ?", (service_id,))
        results = cursor.fetchall()
        conn.close()
        return [dict(result) for result in results]

    def get_all_services(self):
        conn = sqlite3.connect(self.user_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, category, title, description, username FROM services WHERE status = ?",
            (ServiceStatus.ACTIVE.value,),
        )
        results = cursor.fetchall()
        conn.close()
        return [dict(result) for result in results]

    def get_all_services_by_category(self, category: str):
        if category in iter(ServiceCategory):
            conn = sqlite3.connect(self.user_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, description, username FROM services WHERE status = ? AND category = ?",
                (ServiceStatus.ACTIVE.value, category),
            )
            result = cursor.fetchall()
            conn.close()
            return result
        return self.get_all_services()

    def remove_service(self, username: str, service_id: int):
        conn = sqlite3.connect(self.user_db)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM services WHERE username = ? AND id = ?", (username, service_id))
        cursor.execute(
            "DELETE FROM images WHERE serviceId = ?", (service_id,)
        )  # TODO Am I able to delete images of a different user?
        conn.commit()
        conn.close()

    def update_service(
        self,
        username: str,
        service_id: int,
        title: str,
        description: str,
        category: str,
        availability: int,
        images: list,
    ):
        conn = sqlite3.connect(self.user_db)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE services SET title = ?, description = ?, category = ?, availability = ? WHERE username = ? AND id = ?",
            (title, description, category, availability, username, service_id),
        )
        # Delete images and reupload them on update, probably should be improved
        cursor.execute("DELETE FROM images WHERE serviceId = ?", (service_id,))
        # TODO Am I able to delete images of a different user?
        for image in images:
            cursor.execute(
                "INSERT INTO images (serviceId, filename, filenameOnServer) VALUES (?, ?, ?)",
                (service_id, image["filename"], image["filenameOnServer"]),
            )
        conn.commit()
        conn.close()
        return self.get_service_by_id(service_id)

    def _update_service_status(self, username: str, service_id: int, status: str):
        conn = sqlite3.connect(self.user_db)
        cursor = conn.cursor()
        cursor.execute("UPDATE services SET status = ? WHERE username = ? AND id = ?", (status, username, service_id))
        conn.commit()
        conn.close()

    def activate_service(self, username: str, service_id: int):
        self._update_service_status(username, service_id, ServiceStatus.ACTIVE.value)

    def pause_service(self, username: str, service_id: int):
        self._update_service_status(username, service_id, ServiceStatus.PAUSED.value)

    def add_booking(self, service_id: int, tutor_id: int, student_id: int, datetime: str, duration: int):
        conn = sqlite3.connect(self.user_db)
        cursor = conn.cursor()
        sql = "INSERT INTO bookings (serviceId, tutorId, studentId, status, datetime, durationMinutes) VALUES(?, ?, ?, ?, ?, ?)"
        cursor.execute(sql, (service_id, tutor_id, student_id, BookingStatus.PENDING, datetime, duration))
        booking_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return booking_id

    def _update_booking_status(self, user_id: int, booking_id: int, status: BookingStatus):
        conn = sqlite3.connect(self.user_db)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE bookings SET status = ? WHERE id = ? AND (tutorId = ? OR studentId = ?)",
            (status, booking_id, user_id, user_id),
        )
        conn.commit()
        conn.close()

    def confirm_booking(self, user_id: int, booking_id: int):
        self._update_booking_status(user_id, booking_id, BookingStatus.CONFIRMED)

    def cancel_booking(self, user_id: int, booking_id: int):
        self._update_booking_status(user_id, booking_id, BookingStatus.CANCELLED)

    def get_bookings_for_user(self, user_id: int):
        conn = sqlite3.connect(self.user_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        sql = """
        SELECT 
            bookings.id, bookings.tutorId, bookings.studentId, bookings.datetime, bookings.durationMinutes, bookings.status, services.title, services.description, services.id as serviceId
        FROM 
            bookings 
        INNER JOIN
            services
        ON
            bookings.serviceId = services.id  
        WHERE
            tutorId = ? OR studentId = ?
        ORDER BY
            datetime
        """
        cursor.execute(sql, (user_id, user_id))
        results = cursor.fetchall()
        conn.close()
        return [dict(result) for result in results]

    def get_bookings_between_users(self, user_id: int, peer_id: int):
        conn = sqlite3.connect(self.user_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        sql = f"""
        SELECT 
            bookings.id, bookings.tutorId, bookings.studentId, bookings.datetime, bookings.durationMinutes, services.title, services.description, services.id as serviceId
        FROM 
            bookings 
        INNER JOIN
            services
        ON
            bookings.serviceId = services.id  
        WHERE
            ((tutorId = ? AND studentId = ?) OR (tutorId = ? AND studentId = ?)) AND bookings.status = '{BookingStatus.CONFIRMED}'
        ORDER BY
            datetime
        """
        cursor.execute(sql, (user_id, peer_id, peer_id, user_id))
        results = cursor.fetchall()
        conn.close()
        return [dict(result) for result in results]
