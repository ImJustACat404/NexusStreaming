__author__ = "Ido Senn"

import sqlite3
import hashlib
import os
import threading


DATABASE_LOCATION = "DB/UserData.db"
DB_LOCK = threading.Lock()


def hash_data(data, salt):
    """
    A function that runs data threw sha256
    :param data: The data to hash
    :type data: str
    :param salt: A value used to make sure similar data won't result in the same output
    :type salt: bytes
    :return: The hashed data
    :rtype: hex
    """
    sha256_hash = hashlib.pbkdf2_hmac('sha256', data.encode(), salt, 100000)
    return sha256_hash.hex()


def is_email_in_system(user_email):
    """
    A function that returns True if an email address is in the database, and False otherwise
    :param user_email: The client's email address
    :type user_email: str
    :return: True if an email address is in the database, and False otherwise
    :rtype: bool
    """
    # print("[-R-] User DB Access")
    with DB_LOCK:
        saved_users_db = sqlite3.connect(DATABASE_LOCATION)
        user_db_cursor = saved_users_db.cursor()
        query = "SELECT Email from Users WHERE Email=?"
        user_db_cursor.execute(query, (user_email,))
        output = user_db_cursor.fetchall()
        user_db_cursor.close()
        saved_users_db.close()
    if len(output) > 0:
        return True
    else:
        return False


def add_user(uname, password, email):
    """
    A function that adds a new user to the database
    :param uname: username
    :type uname: str
    :param password: The chosen password
    :type password: str
    :param email: The client's email address
    :type email: str
    """
    # print("[-W-] User DB Access")
    with DB_LOCK:
        saved_users_db = sqlite3.connect(DATABASE_LOCATION)
        user_db_cursor = saved_users_db.cursor()
        salt = os.urandom(32)  # creates salt for the user
        # Add new user
        query = "INSERT INTO Users (UName, Password, Email, Salt) VALUES (?, ?, ?, ?)"
        user_db_cursor.execute(query, (uname, hash_data(password, salt), email, salt))
        saved_users_db.commit()
        user_db_cursor.close()
        saved_users_db.close()


def validate_password(input_password, user_email):
    """
    A function that validates an input password with the one in the database
    :param input_password: The password to validate
    :type input_password: str
    :param user_email: The user's email address
    :type user_email: str
    :return: True if the password is correct, false otherwise
    :rtype: bool
    """
    # print("[-R-] User DB Access")
    with DB_LOCK:
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
    """
    A function that returns the username for a given email address
    :param email: The user's email address
    :type email: str
    :return: The client's username
    :rtype: str
    """
    # print("[-R-] User DB Access")
    with DB_LOCK:
        saved_users_db = sqlite3.connect(DATABASE_LOCATION)
        user_db_cursor = saved_users_db.cursor()
        query = "SELECT UName FROM Users WHERE Email = ?"
        user_db_cursor.execute(query, (email,))
        uname = (user_db_cursor.fetchall())[0][0]
        user_db_cursor.close()
        saved_users_db.close()
    return uname


