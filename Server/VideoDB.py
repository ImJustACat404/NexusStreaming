__author__ = "Ido Senn"

import sqlite3
import threading


DATABASE_LOCATION = "DB/UserData.db"
DB_EDIT_LOCK = threading.Lock()


def add_video(video_name, creator):
    with DB_EDIT_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        db_cursor.execute("INSERT INTO Videos (Name, Creator, Likes, Dislikes, views) VALUES (?, ?, ?, ?, ?)",
                          (video_name, creator, 0, 0, 0))
        video_id = db_cursor.lastrowid
        database.commit()
        db_cursor.close()
        database.close()
    return video_id


def get_latest():
    database = sqlite3.connect(DATABASE_LOCATION)
    db_cursor = database.cursor()
    query = "SELECT Name, Creator, Likes, Dislikes, Views, VideoID from Videos ORDER BY VideoID DESC LIMIT 45"
    db_cursor.execute(query)
    last_45_videos = db_cursor.fetchall()
    db_cursor.close()
    database.close()
    return last_45_videos


def search_video(keyword):
    database = sqlite3.connect(DATABASE_LOCATION)
    db_cursor = database.cursor()
    query = 'SELECT Name, Creator, Likes, Dislikes, Views, VideoID from Videos WHERE Name LIKE ? LIMIT 45'
    db_cursor.execute(query, ('%' + keyword + '%',))
    last_45_videos = db_cursor.fetchall()
    db_cursor.close()
    database.close()
    return last_45_videos


def get_video_data(video_id):
    database = sqlite3.connect(DATABASE_LOCATION)
    db_cursor = database.cursor()
    query = 'SELECT Name, Creator, Likes, Dislikes, Views from Videos WHERE VideoID = ?'
    db_cursor.execute(query, (video_id,))
    video_data = db_cursor.fetchone()
    db_cursor.close()
    database.close()
    return video_data


def add_likes(video_id, likes_to_add):
    with DB_EDIT_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "UPDATE Videos SET [Likes] = [Likes] + ? WHERE VideoID = ?"
        db_cursor.execute(query, (likes_to_add, video_id))
        database.commit()
        db_cursor.close()
        database.close()


def add_dislikes(video_id, dislikes_to_add):
    with DB_EDIT_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "UPDATE Videos SET [Dislikes] = [Dislikes] + ? WHERE VideoID = ?"
        db_cursor.execute(query, (dislikes_to_add, video_id))
        database.commit()
        db_cursor.close()
        database.close()


def add_views(video_id, views_to_add):
    with DB_EDIT_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "UPDATE Videos SET [Views] = [Views] + ? WHERE VideoID = ?"
        db_cursor.execute(query, (views_to_add, video_id))
        database.commit()
        db_cursor.close()
        database.close()


def is_video_in_db(video_id):
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
    with DB_EDIT_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "DELETE FROM Videos WHERE VideoID = ?"
        db_cursor.execute(query, (video_id,))
        database.commit()
        db_cursor.close()
        database.close()



