__author__ = "Ido Senn"

import UserDB
import VideoDB
import Communication
import socket
import threading
import select
from ServerObjects import User
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from AESEncrypt import AESCypher


PORT = 8009
CONNECTED_USERS = {}
OPEN_STREAMS_USERS = {}


def broadcast(creator, video_id):
    global OPEN_STREAMS_USERS
    views_old = 0
    stream_open = True
    while stream_open:
        ready_to_read, ready_to_write, in_error = select.select(OPEN_STREAMS_USERS[video_id] + [creator.get_socket()], OPEN_STREAMS_USERS[video_id], [])
        likes_to_add = 0
        dislikes_to_add = 0
        for read_socket in ready_to_read:
            read_user = CONNECTED_USERS[read_socket]
            message = read_user.recv_message()
            if read_user is creator:
                # Either close request or stream frame \ audio
                if message["type"] == "close":
                    VideoDB.remove_video(video_id)
                    for client_socket in ready_to_write:
                        client = CONNECTED_USERS[client_socket]
                        message = {"type": "close"}
                        client.send_message(message)  # maybe some users won't be disconnected
                        threading.Thread(target=new_user, args=(client,)).start()
                    threading.Thread(target=new_user, args=(creator,)).start()
                    stream_open = False
                else:
                    for write_socket in ready_to_write:
                        write_user = CONNECTED_USERS[write_socket]
                        write_user.send_message(message)
            else:
                if message["type"] == "like":
                    likes_to_add += 1
                elif message["type"] == "dislike":
                    dislikes_to_add += 1
                elif message["type"] == "close":
                    OPEN_STREAMS_USERS[video_id].remove(read_socket)
                    if read_socket in ready_to_write:
                        ready_to_write.remove(read_socket)
                    message = {"type": "close"}
                    read_user.send_message(message)  # maybe some users won't be disconnected
                    threading.Thread(target=new_user, args=(read_user,)).start()
        if likes_to_add != 0:
            VideoDB.add_likes(video_id, likes_to_add)
        if dislikes_to_add != 0:
            VideoDB.add_dislikes(video_id, dislikes_to_add)
        if views_old != len(OPEN_STREAMS_USERS[video_id]):
            VideoDB.add_views(video_id, len(OPEN_STREAMS_USERS[video_id]) - views_old)
            views_old = len(OPEN_STREAMS_USERS[video_id])


def new_broadcaster(user, request):
    print(f"new streamer: {user.get_uname()}")
    video_id = VideoDB.add_video(request["title"], user.get_uname())
    OPEN_STREAMS_USERS[video_id] = []
    broadcast(user, video_id)


def user_search(user, request):
    if request["keyword"] == "":
        video_list = VideoDB.get_latest()
    else:
        video_list = VideoDB.search_video(request["keyword"])
    message = {"type": "result", "results": video_list}
    user.send_message(message)


def new_watcher(user, request):
    video_id = -1
    selected_a_video = False
    while not selected_a_video:
        if request["type"] == "search":
            user_search(user, request)
            request = user.recv_message()
        elif request["type"] == "watch":
            # block people from opening closed streams
            if VideoDB.is_video_in_db(request["vid"]):
                video_id = request["vid"]
                message = {"type": "status", "status": True, "text": f"Connected to stream {video_id}"}
                user.send_message(message)
                selected_a_video = True
            else:
                message = {"type": "status", "status": False, "text": "Video not found!"}
                user.send_message(message)
                request = user.recv_message()
        else:
            pass
    OPEN_STREAMS_USERS[video_id] += [user.get_socket()]


def new_user(user):
    # Check if broadcaster or watcher
    global CONNECTED_USERS
    try:
        request = user.recv_message()
        # either a request for a video list of the creation of a new stream
        if request["type"] == "broadcast":
            new_broadcaster(user, request)
        elif request["type"] == "search":
            new_watcher(user, request)
        else:
            pass  # invalid request
    except RuntimeError:
        pass  # socket closed


def sign_up(request):
    # Errors: Successful = 0, Email already in system = 1
    if UserDB.is_email_in_system(request["email"]):
        return False, "Email already in system"
    if len(request["password"]) < 6:
        return False, "Password must be at least 6 characters long"
    else:
        # Add new user
        UserDB.add_user(request["uname"], request["password"], request["email"])
        return True, "Sign up successful"


def log_in(request):
    # Errors: Successful = 0, No email in system = 1, wrong password = 2
    if not UserDB.is_email_in_system(request["email"]):
        return False, "Email not in system"
    else:
        if UserDB.validate_password(request["password"], request["email"]):
            return True, "Login successful"
        else:
            return False, "Wrong password"


def try_connecting(request):
    if request["type"] == "login":
        status, text = log_in(request)
    elif request["type"] == "signup":
        status, text = sign_up(request)
    else:
        status = False
        text = "Invalid operation"
    return status, text


def connect(client_socket, aes_cypher):
    # Handle case where request isn't login or signup
    successful = False
    request = {}

    try:
        while not successful:
            request = Communication.recv_message_aes(client_socket, aes_cypher)
            successful, text = try_connecting(request)
            message = {"type": "status", "status": successful, "text": text}
            Communication.send_message_aes(client_socket, message, aes_cypher)

        # Get user data from database
        email = request["email"]
        uname = UserDB.get_user_name(email)

        print(f"New user! User name: {uname}, E-Mail: {email}")
        CONNECTED_USERS[client_socket] = User(client_socket, uname, email, aes_cypher)
        new_user(CONNECTED_USERS[client_socket])
    except RuntimeError:
        pass  # socket closed


def establish_secure_connection(client_socket):
    private_key, public_key = Communication.generate_rsa_keys()
    message = {"type": "rsa_key", "key": public_key}
    Communication.send_message_unsecure(client_socket, message)
    rsa_cypher = PKCS1_OAEP.new(RSA.importKey(private_key))
    message = Communication.recv_message_rsa(client_socket, rsa_cypher)
    aes_key = message["key"]
    aes_iv = message["iv"]
    aes_cypher = AESCypher(aes_iv, aes_key)
    connect(client_socket, aes_cypher)


def main():
    # Connect to clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', PORT))  # Bind to a specific address and port
    server_socket.listen()  # Listen for incoming connections
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connected to client {client_address}")
        threading.Thread(target=establish_secure_connection, args=(client_socket,)).start()


if __name__ == "__main__":
    main()
