import mysql.connector
from contextlib import contextmanager

host = "by9wci4kqxkcw6o4tihu-mysql.services.clever-cloud.com" 
user = "uczfo9spvbt3dmse"
password = "RQi2tHBt1sIBp0nkPTQe"
database = "by9wci4kqxkcw6o4tihu"

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
        
        return True if user else False



def register_user(username, email, password, role_id):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO Users (username, email, password, role_id) VALUES (%s, %s, %s, %s)",
            (username, email, password, role_id)
        )

def login_user(email, password):
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT username FROM Users WHERE email=%s and password=%s",(email, password)
        )
        user = cursor.fetchall()
        return len(user) == 1



if __name__ == "__main__":
    pass
    # register_user("Jey", "jey@email.com", "password", 2)
    # # products = login_user("admin@example.com", "password")
    # # print(products)