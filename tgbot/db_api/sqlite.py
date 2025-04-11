import sqlite3


class Database:
    def __init__(self, path_to_db="main.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = (), fetchone: bool = False, fetchall: bool = False, commit: bool = False):
        with self.connection as conn:
            cursor = conn.cursor()
            cursor.execute(sql, parameters)
            data = None
            if fetchone:
                data = cursor.fetchone()
            if fetchall:
                data = cursor.fetchall()
            if commit:
                conn.commit()
            return data

    def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
            id int NOT NULL,
            username varchar(255) NOT NULL,
            name varchar(255) NOT NULL,
            PRIMARY KEY (id)
        );
        """
        self.execute(sql, commit=True)

    def add_user(self, id: int, username: str, name: str):
        sql = "INSERT INTO Users(id, username, name) VALUES (?, ?, ?)"
        parameters = (id, username, name)
        self.execute(sql, parameters=parameters, commit=True)

    def select_all_users(self):
        sql = "SELECT * FROM Users"
        return self.execute(sql, fetchall=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([f"{item} = ?" for item in parameters])
        return sql, tuple(parameters.values())

    def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE"
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters, fetchone=True)


    def delete_user(self, **kwargs):
        sql = "DELETE FROM Users WHERE"
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters, fetchone=True)

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM Users;", fetchone=True)

    def get_all_user_ids(self):
        return self.execute("SELECT id FROM Users", fetchall=True)
