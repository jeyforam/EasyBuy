import os
import sys
import mysql.connector
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_DATABASE")


@contextmanager
def get_db_cursor(commit=False):
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    cursor = connection.cursor(dictionary=True)
    yield cursor

    if commit:
        connection.commit()
    
    cursor.close()
    connection.close()