import sqlite3
import os


DATABASE_NAME = 'database.db'
with open('database_squema.sql', 'r') as sql_file:
    DATABASE_SCHEMA = sql_file.read()


class Database:
    """
    Singleton class that handles database connections and
    database functionality.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Creates a new instance of the database if it doesn't already exist. If the
        database instance already exists, returns the existing one instead of creating
        a new one.
        """
        if not cls._instance:
            cls._instance = object.__new__(cls)
            cls._instance.__initialized = False
            return cls._instance
        else:
            return cls._instance

    def __init__(self):
        """
        If the database instance (singleton) is instantiated, it creates the database
        connection and cursor. If the database file doesn't exist already, create the
        database and its schema.
        """
        if self.__initialized:
            return
        db_exists = os.path.exists(DATABASE_NAME)
        self._connection = sqlite3.connect(DATABASE_NAME)
        self._cursor = self._connection.cursor()
        if not db_exists:
            self._create_schema()
        self._initialized = True

    def query(self, sql, params):
        self.cursor.execute(sql, params)
        self.connection.commit()

    def select_query(self, query):
        res = self.cursor.execute(query)
        return res.fetchall()


    @property
    def cursor(self):
        return self._cursor

    @property
    def connection(self):
        return self._connection

    def _create_schema(self):
        """
        If the database is being created, it executes the SQL code to create
        the database schema.
        :return:
        """
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

