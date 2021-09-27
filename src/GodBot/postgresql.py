""" Handle RDS postgreSQL database """


import os

from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from GodBot.exceptions import NoEnvException


def connect_to_db():
    "connect to database and return the cursor"
    try:
        load_dotenv()
        host = os.getenv("RDS_DB_HOST")
        if host is None:
            raise NoEnvException("RDS_DB_HOST")
        password = os.getenv("RDS_DB_PWD")
        if password is None:
            raise NoEnvException("RDS_DB_PWD")
        database = psycopg2.connect(
            host=host, database="godbot", user="postgres", password=password)
        return database.cursor(cursor_factory=psycopg2.extras.DictCursor), database
    except psycopg2.Error as err:
        print(err)
    except NoEnvException as err:
        print(err)
    return None, None


def db_command(sqlcommand: str, cmd_datas: tuple=()):
    "execute a command inside the database and return the result"
    cursor, database = connect_to_db()
    if cursor is not None:
        cursor.execute(sqlcommand, cmd_datas)
        try:
            fetch = cursor.fetchall()
        except psycopg2.ProgrammingError:
            fetch = []
        database.commit()
        cursor.close()
        database.close()
        return fetch
    return []


def db_insert_rows(table: str, rows: list[tuple]):
    "execute a command inside the database and return the result"
    cursor, database = connect_to_db()
    if cursor is not None:
        nb_value_str = "("
        for _ in enumerate(rows[0]):
            nb_value_str += "%s,"
        nb_value_str = nb_value_str.removesuffix(",") + ")"
        execute_arg = ','.join(cursor.mogrify(nb_value_str, row).decode("utf-8") for row in rows)
        cursor.execute(f"insert into {table} values " + execute_arg)
        database.commit()
        cursor.close()
        database.close()
