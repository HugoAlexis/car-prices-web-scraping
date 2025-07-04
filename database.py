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
        self.use_postgres = use_postgres
        if use_postgres:
            self._initialize_db_postgres()
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
        if not already_exists:
            self._create_schema()


    def query(self, sql, params):
        if self.use_postgres:
            sql = sql.replace('?', '%s')

        self.cursor.execute(sql, params)
        self.connection.commit()

    def select_query(self, query):
        res = self.cursor.execute(query)
        return res.fetchall()

    def select(self, table, columns='*', where_clause=None, where_params=None, verbose=False, return_column_names=False):
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

        if self.use_postgres:
            query = query.replace('?', '%s')

        if verbose:
            print(query)
        self.cursor.execute(query, where_params or [])
        column_names = [desc[0] for desc in self.cursor.description]
        if return_column_names:
            return column_names, self.cursor.fetchall()
        return self.cursor.fetchall()

    def insert(self, table, values, ignore_protected=True):
        if ignore_protected:
            values = values.copy()
            key_values = list(values.keys())
            for key in key_values:
                if key.startswith('_'):
                    values.pop(key)

        n_values = len(values)
        columns = ', '.join(values.keys())
        params = list(values.values())
        sql = (
            f'INSERT INTO {table}\n'
            f'({columns})\nVALUES '
            '(' + '?, ' * (n_values - 1) + '?)'
        )

        if self.use_postgres:
            sql = sql.replace('?', '%s')

        self.query(sql, params)

    def update(self, table, values, ignore_protected=True, where_clause=None, where_params=None):
        if ignore_protected:
            values = values.copy()
            key_values = list(values.keys())
            for key in key_values:
                if key.startswith('_'):
                    values.pop(key)

        sets_clauses = ', '.join([f'{col} = \'{value}\'' for col, value in values.items()])

        sql = (
            f'UPDATE {table}\n' 
            f'SET {sets_clauses}\n'
            f'WHERE {where_clause}'
        )

        if self.use_postgres:
            sql = sql.replace('?', '%s')

        self.query(sql, where_params or [])

    def get_item_match(self, table_name, item_values):
        columns = list(item_values.keys())
        values = list(item_values.values())
        where_clause = '\n'.join([f'{col} = ?' for col in columns])
        column_names, db_item =  self.select(
            table_name,
            where_clause=where_clause,
            where_params=values,
            return_column_names=True)
        if db_item:
            return dict(zip(column_names, db_item[0]))
        else:
            return None

    @property
    def cursor(self):
        return self._cursor

    @property
    def connection(self):
        return self._connection

    def _create_schema(self, cursor=None):
        """
        If the database is being created, it executes the SQL code to create
        the database schema.
        :return:
        """
        print('Initializing Database!')
        cursor = cursor or self.cursor
        if self.use_postgres:
            cursor.execute(DATABASE_SCHEMA)
        else:
            cursor.executescript(DATABASE_SCHEMA)
        self._connection.commit()



db = Database(use_postgres=True)

