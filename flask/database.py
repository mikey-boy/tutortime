import sqlite3
import os.path
import hashlib
from enum import StrEnum, auto

def _crud(db:str, query: str):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()

class ServiceStatus(StrEnum):
    ACTIVE = auto()
    PAUSED = auto()
    DRAFT = auto() 

class ServiceCategory(StrEnum):
    LANGUAGE = auto()
    MUSIC = auto()
    SOFTWARE = auto()
    WELLNESS = auto()
    OTHER = auto()

class Database:
    def __init__(self, user_db: str, service_db: str):
        self.user_db = user_db
        self.service_db = service_db

        user_schema = """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT
            )
            """
        service_schema = """
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY,
                username TEXT,
                title TEXT, 
                description TEXT,
                category TEXT,
                status TEXT,
                hoursGiven INTEGER
            )
        """
        
        _crud(self.user_db, user_schema)
        _crud(self.service_db, service_schema)

    def user_exists(self, username: str):
        conn = sqlite3.connect(self.user_db)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
        
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
            cursor.execute("INSERT INTO users VALUES(?, ?)", (username, encoded_pass))
            conn.commit()
            conn.close()

    def remove_user(self, username:str):
        if self.user_exists(username):
            conn = sqlite3.connect(self.user_db)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
            conn.close()

    def add_service(self, username:str, title:str, description:str, category:str):
        if category in iter(ServiceCategory):
            conn = sqlite3.connect(self.service_db)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO services (username, title, description, category, status, hoursGiven) VALUES(?, ?, ?, ?, ?, ?)", (username, title, description, category, ServiceStatus.ACTIVE, 0))
            conn.commit()
            conn.close()

    def get_services_by_status(self, username:str, status: str):
        if status in iter(ServiceStatus):
            conn = sqlite3.connect(self.service_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, description FROM services WHERE username = ? AND status = ?", (username, status))
            result = cursor.fetchall()
            conn.close()
            return result

    def get_service_by_id(self, username:str, service_id:int):
        conn = sqlite3.connect(self.service_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description FROM services WHERE username = ? AND id = ?", (username, service_id))
        result = cursor.fetchone()
        conn.close()
        return result

    def get_all_services(self):
        conn = sqlite3.connect(self.service_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT title, description, username FROM services WHERE status = ?", (ServiceStatus.ACTIVE.value,))
        result = cursor.fetchall()
        conn.close()
        return result
    
    def get_all_services_by_category(self, category:str):
        if category in iter(ServiceCategory):
            conn = sqlite3.connect(self.service_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT title, description, username FROM services WHERE status = ? AND category = ?", (ServiceStatus.ACTIVE.value, category))
            result = cursor.fetchall()
            conn.close()
            return result
        return self.get_all_services()

    def remove_service(self, username:str, service_id:int):
        conn = sqlite3.connect(self.service_db)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM services WHERE username = ? AND id = ?", (username, service_id))
        conn.commit()
        conn.close()

    def update_service(self, username:str, service_id:int, title:str, description:str):
        conn = sqlite3.connect(self.service_db)
        cursor = conn.cursor()
        cursor.execute("UPDATE services SET title = ?, description = ? WHERE username = ? AND id = ?", (title, description, username, service_id))
        conn.commit()
        conn.close()


    def _update_service_status(self, username:str, service_id:int, status:str):
        conn = sqlite3.connect(self.service_db)
        cursor = conn.cursor()
        cursor.execute("UPDATE services SET status = ? WHERE username = ? AND id = ?", (status, username, service_id))
        conn.commit()
        conn.close()

    def activate_service(self, username:str, service_id:int):
        self._update_service_status(username, service_id, ServiceStatus.ACTIVE.value)

    def pause_service(self, username:str, service_id:int):
        self._update_service_status(username, service_id, ServiceStatus.PAUSED.value)
    
    def draft_service(self, username:str, service_id:int):
        self._update_service_status(username, service_id, ServiceStatus.DRAFT.value)