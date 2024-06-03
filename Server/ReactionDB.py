__author__ = "Ido Senn"

import sqlite3
import threading


DATABASE_LOCATION = "DB/UserData.db"
DB_LOCK = threading.Lock()


def remove_reaction(vid, user_mail):
    """
    A function that removes a reaction from the database
    :param vid: Video ID of the stream
    :type vid: int
    :param user_mail: The client's email address
    :type user_mail: str
    """
    print("[-W-] Reaction DB Access")
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "DELETE FROM Reactions WHERE VID = ? AND UserEmail = ?"
        db_cursor.execute(query, (vid, user_mail))
        database.commit()
        db_cursor.close()
        database.close()


def add_reaction(vid, user_mail, reaction):
    """
    A function that adds a reaction to the database
    :param vid: Video ID of the stream
    :type vid: int
    :param user_mail: The client's email address
    :type user_mail: str
    :param reaction: The reaction to add (1 - like, -1 - dislike)
    :type reaction: int
    """
    print("[-W-] Reaction DB Access")
    # remove current reaction
    remove_reaction(vid, user_mail)
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "INSERT INTO Reactions (UserEmail, VID, Reaction) VALUES (?, ?, ?)"
        db_cursor.execute(query, (user_mail, vid, reaction))
        database.commit()
        db_cursor.close()
        database.close()


def remove_all_reactions_user(user_mail):
    """
    A function that removes all the reactions for a specific user
    :param user_mail: The client's email address
    :type user_mail: str
    """
    print("[-W-] Reaction DB Access")
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "DELETE FROM Reactions WHERE UserEmail = ?"
        db_cursor.execute(query, (user_mail,))
        database.commit()
        db_cursor.close()
        database.close()


def remove_all_reactions_video(vid):
    """
    A function that removes all the reactions for a specific stream
    :param vid: Video ID of the stream
    :type vid: int
    """
    print("[-W-] Reaction DB Access")
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "DELETE FROM Reactions WHERE VID = ?"
        db_cursor.execute(query, (vid,))
        database.commit()
        db_cursor.close()
        database.close()


def get_reaction(vid, user_mail):
    """
    Get reaction for a specific client, for a specific stream
    :param vid: Video ID of the stream
    :type vid: int
    :param user_mail: The client's email address
    :type user_mail: str
    :return: The client's reaction
    :rtype: int
    """
    print("[-R-] Reaction DB Access")
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = 'SELECT Reaction from Reactions WHERE VID = ? AND UserEmail = ?'
        db_cursor.execute(query, (vid, user_mail))
        reaction = db_cursor.fetchone()
        db_cursor.close()
        database.close()
    if reaction is None:
        return 0
    else:
        return reaction[0]


def how_many_likes(vid):
    """
    A function that returns the number of likes for a specific stream
    :param vid: Video ID of the stream
    :type vid: int
    :return: A list of the stream's reactions
    """
    print("[-R-] Reaction DB Access")
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = 'SELECT Reaction from Reactions WHERE VID = ? AND Reaction = 1'
        db_cursor.execute(query, (vid,))
        output = db_cursor.fetchall()
        db_cursor.close()
        database.close()
    return len(output)


def how_many_dislikes(vid):
    """
    A function that returns the number of dislikes for a specific stream
    :param vid: Video ID of the stream
    :type vid: int
    :return: A list of the stream's reactions
    """
    print("[-R-] Reaction DB Access")
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = 'SELECT Reaction from Reactions WHERE VID = ? AND Reaction = -1'
        db_cursor.execute(query, (vid,))
        output = db_cursor.fetchall()
        db_cursor.close()
        database.close()
    return len(output)
