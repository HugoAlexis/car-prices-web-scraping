import sqlite3
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv('.env')

DATABASE_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

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

    def __init__(self, use_postgres=False):
        """
        If the database instance (singleton) is instantiated, it creates the database
        connection and cursor. If the database file doesn't exist already, create the
        database and its schema.
        """
        if self.__initialized:
            return

        # Initialize chosen database (postgres or sqlite)
        self._initialized = False
        if use_postgres:
            self._initialize_db_postgres()
            self.use_postgres = True
        if not self._initialized:
            self._initialize_db_sqlite()
            self.use_postgres = False

    def _initialize_db_sqlite(self):
        """
        Initializes the SQLite database, connection and cursor.
        Creates the database if it doesn't already exist.'

        :return: None
        """
        db_fullname = f'{DATABASE_NAME}.sqlite'
        db_exists = os.path.exists(db_fullname)
        self._connection = sqlite3.connect(db_fullname)
        self._cursor = self._connection.cursor()
        if not db_exists:
            self._create_schema()
        self._initialized = True
        print('Using DB SQLite')

    def _initialize_db_postgres(self):
        """
        Initializes the PostgreSQL database, connection and cursor.
        Creates the database if it doesn't already exist.'

        :return: None
        :return:
        """
        try:
            conn = psycopg2.connect(
                dbname='postgres',
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute(f'SELECT 1 FROM pg_database WHERE datname ILIKE \'{DATABASE_NAME}\';')
                already_exists = len(cursor.fetchall()) > 0
                if not already_exists:
                    cursor.execute(f'CREATE DATABASE {DATABASE_NAME};')
                    print('PostgreSQL Database Created')
            conn.close()
        except psycopg2.OperationalError:
            print('PostgreSQL connection failed. Using SQLite instead')
            return
        self._connection = psycopg2.connect(
            dbname=DATABASE_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        self._cursor = self._connection.cursor()
        self._initialized = True


    def query(self, sql, params):
        self.cursor.execute(sql, params)
        self.connection.commit()

    def select_query(self, query):
        res = self.cursor.execute(query)
        return res.fetchall()

    def select(self, table, columns='*', where_clause=None, where_params=None):
        """
           Executes a safe SELECT query on the database.

           Args:
               table (str): Name of the table.
               columns (list): List of columns to select.
               where_clause (str, optional): WHERE condition with placeholders.
               where_params (tuple or list, optional): Parameters for the WHERE clause.

           Returns:
               list: Query results.
           """
        cols = ', '.join(columns)
        query = f"SELECT {cols} FROM {table}"

        if where_clause:
            query += f" WHERE {where_clause}"

        self.cursor.execute(query, where_params or [])
        return self.cursor.fetchall()


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
    db = Database(use_postgres=True)

