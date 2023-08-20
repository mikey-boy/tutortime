import sqlite3
import os.path
import hashlib

def _crud(db:str, query: str):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()

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

    def add_service(self, username:str, title:str, description:str):
        conn = sqlite3.connect(self.service_db)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO services (username, title, description, status, hoursGiven) VALUES(?, ?, ?, ?, ?)", (username, title, description, "active", 0))
        conn.commit()
        conn.close()

    def get_services(self, username:str, status: str):
        conn = sqlite3.connect(self.service_db)
        cursor = conn.cursor()
        cursor.execute("SELECT title, description FROM services WHERE username = ? AND status = ?", (username, status))
        result = cursor.fetchall()
        print(result)
        conn.close()
        return result


    def remove_service(self):
        pass
