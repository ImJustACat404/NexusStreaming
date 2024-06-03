__author__ = "Ido Senn"

import UserDB
import VideoDB
import ReactionDB
import Communication
import socket
import threading
import ServerUser
from ServerUser import User
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from AESEncrypt import AESCypher
import random
import EmailService


PORT = 8001
CONNECTED_USERS = {}  # sockets as keys and users as values
OPEN_STREAMS_USERS = {}  # Video id is key and watcher list is value


def close_user(user):
    """
    A function that disconnects a user
    :param user: The user to disconnect
    :type user: User
    """
    CONNECTED_USERS.pop(user.get_socket())
    user.get_socket().close()
    print(f"Client {user.get_uname()} disconnected")


def broadcast(creator, video_id):
    """
    A function responsible for handling a stream
    :param creator: The user who created the stream
    :type creator: User
    :param video_id: ID of the stream
    :type video_id: int
    """
    max_views = 0
    global OPEN_STREAMS_USERS
    views_old = 0
    stream_open = True
    stream_name = VideoDB.get_video_data(video_id)[0]
    while stream_open:
        read_users, write_users, error_users = ServerUser.user_select(CONNECTED_USERS, OPEN_STREAMS_USERS[video_id] + [creator.get_socket()], OPEN_STREAMS_USERS[video_id], [])
        for read_user in read_users:
            if read_user is creator:
                # A message from the creator
                try:
                    message = read_user.recv_message()
                    # Either close request or stream frame \ audio
                    if message["type"] == "close":
                        # Creator closes stream
                        VideoDB.remove_video(video_id)
                        for write_user in write_users:  # Disconnect all watchers
                            message = {"type": "close"}
                            write_user.send_message(message)
                            threading.Thread(target=new_user, args=(write_user,)).start()  # Send to new thread
                        threading.Thread(target=new_user, args=(creator,)).start()
                        stream_open = False
                    else:
                        # New frame or audio, send to all watchers
                        for write_user in write_users:
                            write_user.send_message(message)
                except Exception as error:
                    # invalid message or Client socket closed
                    print(f"Unexpected input! {error}")
                    # creator socket closed
                    VideoDB.remove_video(video_id)
                    if read_user in read_users:
                        read_users.remove(read_user)
                    for write_user in write_users:  # Disconnect all watchers
                        message = {"type": "close"}
                        write_user.send_message(message)  # maybe some users won't be disconnected
                        threading.Thread(target=new_user, args=(write_user,)).start()
                    close_user(creator)
                    stream_open = False
            else:
                try:
                    # A message from the user
                    message = read_user.recv_message()
                    if message["type"] == "reaction":
                        if message["reaction"] == "like":
                            ReactionDB.add_reaction(video_id, read_user.get_email(), 1)
                        elif message["reaction"] == "dislike":
                            ReactionDB.add_reaction(video_id, read_user.get_email(), -1)
                        elif message["reaction"] == "remove":
                            ReactionDB.remove_reaction(video_id, read_user.get_email())
                    elif message["type"] == "close":
                        OPEN_STREAMS_USERS[video_id].remove(read_user.get_socket())
                        if read_user in write_users:
                            write_users.remove(read_user)
                        message = {"type": "close"}
                        read_user.send_message(message)  # maybe some users won't be disconnected
                        threading.Thread(target=new_user, args=(read_user,)).start()
                except Exception as error:
                    # invalid message or Client socket closed
                    print(f"Unexpected input! {error}")
                    OPEN_STREAMS_USERS[video_id].remove(read_user.get_socket())
                    if read_user in write_users:
                        write_users.remove(read_user)
                    close_user(read_user)
        if views_old != len(OPEN_STREAMS_USERS[video_id]):
            VideoDB.add_views(video_id, len(OPEN_STREAMS_USERS[video_id]) - views_old)
            views_old = len(OPEN_STREAMS_USERS[video_id])
            if len(OPEN_STREAMS_USERS[video_id]) > max_views:
                max_views = len(OPEN_STREAMS_USERS[video_id])
    # send stream summery to the creator
    OPEN_STREAMS_USERS.pop(video_id)
    likes = ReactionDB.how_many_likes(video_id)
    dislikes = ReactionDB.how_many_dislikes(video_id)
    EmailService.stream_summery(creator.get_email(), creator.get_uname(), stream_name, max_views, likes, dislikes)
    ReactionDB.remove_all_reactions_video(video_id)


def new_broadcaster(user, request):
    """
    A function responsible for setting up a new stream
    :param user: The stream's creator
    :type user: User
    :param request: The new stream request
    :type request: dict
    """
    print(f"new streamer: {user.get_uname()}")
    video_id = VideoDB.add_video(request["title"], user.get_uname())
    OPEN_STREAMS_USERS[video_id] = []
    broadcast(user, video_id)


def user_search(user, request):
    """
    A function responsible for handling user search requests
    :param user: The searching user
    :type user: User
    :param request: The search request
    :type request: dict
    """
    if request["keyword"] == "":
        video_list = VideoDB.get_latest()
    else:
        video_list = VideoDB.search_video(request["keyword"])
    video_and_reaction_list = []
    for video in video_list:
        # Get reaction data for results
        name, creator, views, vid = video
        likes = ReactionDB.how_many_likes(vid)
        dislikes = ReactionDB.how_many_dislikes(vid)
        current_reaction = ReactionDB.get_reaction(vid, user.get_email())
        video_and_reaction_list += [(name, creator, views, vid, likes, dislikes, current_reaction)]
    message = {"type": "result", "results": video_and_reaction_list}
    user.send_message(message)


def new_watcher(user, request):
    """
    A function responsible for adding a watcher to a stream
    :param user: The watcher
    :type user: User
    :param request: The client's watch request
    """
    video_id = request["vid"]
    OPEN_STREAMS_USERS[video_id] += [user.get_socket()]


def new_user(user):
    """
    A function responsible for handling requests from the client while navigating the menus
    :param user: The user
    :type user: User
    """
    # Check if broadcaster or watcher
    global CONNECTED_USERS
    try:
        request = None
        navigating_menu = True
        while navigating_menu:
            request = user.recv_message()
            # a request for a search, watch, or the creation of a new stream
            if request["type"] == "broadcast":
                navigating_menu = False  # moves to stream menu
            elif request["type"] == "search":
                user_search(user, request)
            elif request["type"] == "watch":
                # block people from opening closed streams
                if VideoDB.is_video_in_db(request["vid"]):
                    video_id = request["vid"]
                    message = {"type": "status", "status": True, "text": f"Connected to stream {video_id}"}
                    user.send_message(message)
                    navigating_menu = False  # moves to player menu
                else:
                    message = {"type": "status", "status": False, "text": "Video not found!"}
                    user.send_message(message)
        # either watcher or streamer
        if request["type"] == "broadcast":
            new_broadcaster(user, request)
        else:
            # watcher
            new_watcher(user, request)
    except ValueError:
        # socket closed
        close_user(user)
    except Exception as error:
        # Client sent invalid messages
        close_user(user)


def sign_up(request):
    """
    A function for checking if signup request is valid
    :param request: The request
    :type request: dict
    """
    # Errors: Successful = 0, Email already in system = 1
    if UserDB.is_email_in_system(request["email"]):
        return False, "Email already in system"
    if len(request["password"]) < 6:
        return False, "Password must be at least 6 characters long"
    if len(request["uname"]) > 10:
        return False, "Username should be no more then 10 characters"
    else:
        # User can be added
        return True, "Email is available and password is valid"


def log_in(request):
    """
    A function for checking if login request is valid
    :param request: The request
    :type request: dict
    """
    # Errors: Successful = 0, No email in system = 1, wrong password = 2
    if not UserDB.is_email_in_system(request["email"]):
        return False, "Email not in system"
    else:
        if UserDB.validate_password(request["password"], request["email"]):
            return True, "Login successful"
        else:
            return False, "Wrong password"


def try_connecting(request):
    """
    A function that checks if a client's connection request is valid
    :param request: The request
    :type request: dict
    :return: The status (if it's valid), a text describing the status further
    :rtype: tuple
    """
    if request["type"] == "login":
        status, text = log_in(request)
    elif request["type"] == "signup":
        status, text = sign_up(request)
    else:
        status = False
        text = "Invalid operation"
    return status, text


def connect(client_socket, aes_cypher):
    """
    A function responsible for handling connection requests from clients
    :param client_socket: The client's socket
    :type client_socket: socket.socket
    :param aes_cypher: An object used to encrypt and decrypt data with aes
    :type aes_cypher: AESCypher
    """
    # Handle case where request isn't login or signup
    successful = False
    request = {}

    while not successful:
        request = Communication.recv_message_aes(client_socket, aes_cypher)
        successful, text = try_connecting(request)
        message = {"type": "status", "status": successful, "text": text}
        Communication.send_message_aes(client_socket, message, aes_cypher)
        if successful and request["type"] == "signup":
            code = str(random.randint(100000, 999999))
            EmailService.send_verification_code(request["email"], code)
            client_code_verification = Communication.recv_message_aes(client_socket, aes_cypher)
            if client_code_verification["type"] == "code" and client_code_verification["code"] == code:
                UserDB.add_user(request["uname"], request["password"], request["email"])
                text = "Verification successful"
                message = {"type": "status", "status": successful, "text": text}
            else:
                successful = False
                text = "Verification failed"
                message = {"type": "status", "status": successful, "text": text}
            Communication.send_message_aes(client_socket, message, aes_cypher)
    # Get user data from database
    email = request["email"]
    uname = UserDB.get_user_name(email)

    print(f"New user! User name: {uname}, E-Mail: {email}")
    CONNECTED_USERS[client_socket] = User(client_socket, uname, email, aes_cypher)
    new_user(CONNECTED_USERS[client_socket])


def establish_secure_connection(client_socket):
    """
    Agree on AES key in a secure way, with RSA encryption
    :param client_socket: The client's socket
    :type client_socket: socket.socket
    """
    try:
        private_key, public_key = Communication.generate_rsa_keys()
        message = {"type": "rsa_key", "key": public_key}
        Communication.send_message_unsecure(client_socket, message)
        rsa_cypher = PKCS1_OAEP.new(RSA.importKey(private_key))
        message = Communication.recv_message_rsa(client_socket, rsa_cypher)
        aes_key = message["key"]
        aes_iv = message["iv"]
        aes_cypher = AESCypher(aes_iv, aes_key)
        connect(client_socket, aes_cypher)
    except Exception as error:
        client_socket.close()
        print(f"Client error: {error}")
        print("Client disconnected")


def main():
    """
    The main function. Accepts connections from new clients.
    :return:
    """
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
