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

def get_user_by_email(email):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM Users WHERE email=%s",(email,))
        user = cursor.fetchone()
        
        return user if user else False

def register_user(username, email, password, role_id, first_name, last_name, phone_number):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO Users (username, email, password, role_id, first_name, last_name, phone_number) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (username, email, password, role_id, first_name, last_name, phone_number)
        )


def login_user(email, password):
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT username FROM Users WHERE email=%s and password=%s",(email, password)
        )
        user = cursor.fetchall()
        return len(user) == 1

def get_all_users():
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM Users"
        )
        users = cursor.fetchall()
        return users