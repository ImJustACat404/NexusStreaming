__author__ = "Ido Senn"

import sqlite3
import hashlib
import os


DATABASE_LOCATION = "DB/UserData.db"


def hash_data(data, salt):
    sha256_hash = hashlib.pbkdf2_hmac('sha256', data.encode(), salt, 100000)
    return sha256_hash.hex()


def is_email_in_system(user_email):
    saved_users_db = sqlite3.connect(DATABASE_LOCATION)
    user_db_cursor = saved_users_db.cursor()
    user_db_cursor.execute(f"SELECT Email from Users WHERE Email=?", (user_email,))
    output = user_db_cursor.fetchall()
    user_db_cursor.close()
    saved_users_db.close()
    if len(output) > 0:
        return True
    else:
        return False


def add_user(uname, password, email):
    saved_users_db = sqlite3.connect(DATABASE_LOCATION)
    user_db_cursor = saved_users_db.cursor()
    salt = os.urandom(32)  # creates salt for the user
    # Add new user
    user_db_cursor.execute("INSERT INTO Users "
                           "(UName, Password, Email, Salt) "
                           "VALUES (?, ?, ?, ?)", (uname, hash_data(password, salt), email, salt))
    saved_users_db.commit()
    user_db_cursor.close()
    saved_users_db.close()


def validate_password(input_password, user_email):
    saved_users_db = sqlite3.connect(DATABASE_LOCATION)
    user_db_cursor = saved_users_db.cursor()
    query = "SELECT Password, Salt from Users WHERE Email = ?"
    user_db_cursor.execute(query, (user_email,))
    output = user_db_cursor.fetchall()
    user_db_cursor.close()
    saved_users_db.close()
    password = output[0][0]
    salt = output[0][1]
    if password == hash_data(input_password, salt):
        return True
    else:
        return False


def get_user_name(email):
    saved_users_db = sqlite3.connect(DATABASE_LOCATION)
    user_db_cursor = saved_users_db.cursor()
    query = "SELECT UName FROM Users WHERE Email = ?"
    user_db_cursor.execute(query, (email,))
    uname = (user_db_cursor.fetchall())[0][0]
    user_db_cursor.close()
    saved_users_db.close()
    return uname


