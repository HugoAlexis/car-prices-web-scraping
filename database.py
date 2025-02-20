import sqlite3
import os


DATABASE_NAME = 'database.db'
with open('database_squema.sql', 'r') as sql_file:
    DATABASE_SCHEMA = sql_file.read()


class Database:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
            cls._instance.__initialized = False
            return cls._instance
        else:
            return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        db_exists = os.path.exists(DATABASE_NAME)
        self._connection = sqlite3.connect(DATABASE_NAME)
        self._cursor = self._connection.cursor()
        if not db_exists:
            self._create_schema()
        self._initialized = True

    @property
    def cursor(self):
        return self._cursor

    @property
    def connection(self):
        return self._connection

    def _create_schema(self):
        print('Initializing Database!')
        self.cursor.executescript(DATABASE_SCHEMA)
        self._connection.commit()


if __name__ == '__main__':
    db = Database()
    db.cursor.execute(
        'INSERT INTO car_item VALUES (?, ?, ?, ?, ?)',
        (1, 'algo.com', 'ford', 'explorer', 2019)
    )
    db._connection.commit()

