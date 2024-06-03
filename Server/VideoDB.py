__author__ = "Ido Senn"

import sqlite3
import threading


DATABASE_LOCATION = "DB/UserData.db"
DB_LOCK = threading.Lock()


def add_video(video_name, creator):
    """
    A function that adds a new video to the database
    :param video_name: The video's title
    :type video_name: str
    :param creator: The name of the creator
    :type creator: str
    :return: The video's ID, for future use with the system
    :rtype: int
    """
    print("[-W-] Video DB Access")
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "INSERT INTO Videos (Name, Creator, views) VALUES (?, ?, ?)"
        db_cursor.execute(query, (video_name, creator, 0))
        video_id = db_cursor.lastrowid
        database.commit()
        db_cursor.close()
        database.close()
    return video_id


def get_latest():
    """
    A function that returns a list of the latest streams
    :return: A list of the most recent streams
    :rtype: list
    """
    print("[-R-] Video DB Access")
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "SELECT Name, Creator, Views, VideoID from Videos ORDER BY VideoID DESC LIMIT 45"
        db_cursor.execute(query)
        last_45_videos = db_cursor.fetchall()
        db_cursor.close()
        database.close()
    return last_45_videos


def search_video(keyword):
    """
    A function that returns a list of videos with titles like the keyword
    :param keyword: a keyword to search
    :type keyword: str
    :return: A list of the most recent streams
    :rtype: list
    """
    print("[-R-] Video DB Access")
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = 'SELECT Name, Creator, Views, VideoID from Videos WHERE Name LIKE ? LIMIT 45'
        db_cursor.execute(query, ('%' + keyword + '%',))
        last_45_videos = db_cursor.fetchall()
        db_cursor.close()
        database.close()
    return last_45_videos


def get_video_data(video_id):
    """
    A function that returns the saved data fpr a specific video
    :param video_id: The video's unique ID
    :type video_id: int
    :return: The saved data for this video
    :rtype: list
    """
    print("[-R-] Video DB Access")
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = 'SELECT Name, Creator, Views from Videos WHERE VideoID = ?'
        db_cursor.execute(query, (video_id,))
        video_data = db_cursor.fetchone()
        db_cursor.close()
        database.close()
    return video_data


def add_views(video_id, views_to_add):
    """
    A function that adds views to a specific video
    :param video_id: The video's unique ID
    :type video_id: int
    :param views_to_add: Number of views to increment the saved value
    :type views_to_add: int
    """
    print("[-W-] Video DB Access")
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "UPDATE Videos SET [Views] = [Views] + ? WHERE VideoID = ?"
        db_cursor.execute(query, (views_to_add, video_id))
        database.commit()
        db_cursor.close()
        database.close()


def is_video_in_db(video_id):
    """
    A function that checks if a video is in the database
    :param video_id: The video's unique ID
    :type video_id: int
    :return: True if the video is in the database, False otherwise
    :rtype: bool
    """
    print("[-R-] Video DB Access")
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = 'SELECT * from Videos WHERE VideoID = ?'
        db_cursor.execute(query, (video_id,))
        output = db_cursor.fetchall()
        db_cursor.close()
        database.close()
    if len(output) > 0:
        return True
    else:
        return False


def remove_video(video_id):
    """
    A function that removes a video from the database
    :param video_id: The video's unique ID
    :type video_id: int
    """
    print("[-W-] Video DB Access")
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "DELETE FROM Videos WHERE VideoID = ?"
        db_cursor.execute(query, (video_id,))
        database.commit()
        db_cursor.close()
        database.close()
