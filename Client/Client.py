__author__ = "Ido Senn"

import pygame
import Forms
from LoginForm import LogInForm
from SignupForm import SignUpForm
from PlayerForm import PlayerForm
from VideoSelectionForm import VideoSelectionForm
from NewStreamForm import NewStreamForm
from WatchOrStreamForm import WatcherOrStreamerForm
from EmailVerfForm import EmailVerifyForm
import socket
import Communication
import ImageStream
import AudioRecord
import AudioPlay
import AESEncrypt
from AESEncrypt import AESCypher
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import PopupService
pygame.init()


SERVER_IP = "127.0.0.1"
SERVER_PORT = 8001

# Form globals
FIRST_FORM = "login"
WINDOW_FORMS = {}
STREAM_OPEN = False
SOFTWARE_CLOSED = False
STREAM_CLOSE_EVENT_PLAY = pygame.USEREVENT + 1
STREAM_CLOSE_EVENT_SEND = pygame.USEREVENT + 2


def close_program(server_socket):
    """
    A function called when the program is being closed
    :return:
    """
    # Close threads
    global STREAM_OPEN, SOFTWARE_CLOSED
    SOFTWARE_CLOSED = True
    STREAM_OPEN = False
    # Close socket
    server_socket.close()
    # Close pygame
    pygame.quit()
    quit()


def video_send_stream(server_socket, aes_cypher, is_screen):
    """
    Sharing video and audio with server
    :param server_socket: socket for server communications
    :type server_socket: socket.socket
    :param aes_cypher: An object used to encrypt and decrypt data using AES
    :type aes_cypher: AESCypher
    :param is_screen: True if the user chose to capture the screen, False otherwise
    :type is_screen: bool
    """
    # stream details: (vid, is_screen)
    global STREAM_OPEN
    # start the camera and mic
    if is_screen:
        vid_stream = ImageStream.ScreenStream()
    else:
        vid_stream = ImageStream.CameraStream()
    audio_stream = AudioRecord.AudioStream()
    STREAM_OPEN = True
    while STREAM_OPEN:  # make it close when press stop
        video_msg = {"type": "frame", "data": vid_stream.get_current_frame()}
        Communication.send_message_aes(server_socket, video_msg, aes_cypher)
        audio_msg = {"type": "audio", "data": audio_stream.get_current_audio()}
        Communication.send_message_aes(server_socket, audio_msg, aes_cypher)
    Communication.send_message_aes(server_socket, {"type": "close"}, aes_cypher)
    audio_stream.terminate()


def video_play_stream(server_socket, aes_cypher):
    """
    Playing video and audio from server
    :param server_socket: socket for server communications
    :type server_socket: socket.socket
    :param aes_cypher: An object used to encrypt and decrypt data using AES
    :type aes_cypher: AESCypher
    """
    audio_stream = AudioPlay.AudioStream()
    global STREAM_OPEN
    STREAM_OPEN = True
    while STREAM_OPEN:
        message = Communication.recv_message_aes(server_socket, aes_cypher)
        if message["type"] == "audio":
            audio_stream.play_audio(message["data"])
        elif message["type"] == "frame":
            WINDOW_FORMS["player"].set_frame(message["data"])
        elif message["type"] == "close":
            STREAM_OPEN = False
    audio_stream.terminate()
    pygame.event.post(pygame.event.Event(STREAM_CLOSE_EVENT_PLAY))


def event_innit(window_forms):
    """
    Initializing click events for all the buttons
    :param window_forms: A dictionary containing all the window forms
    :type window_forms: dict
    """
    window_forms["signup"].button_event_innit(
        lambda: Forms.change_form(window_forms["signup"], window_forms["login"]),
        lambda: Forms.change_form(window_forms["signup"], window_forms["emailVerify"]))
    window_forms["login"].button_event_innit(
        lambda: Forms.change_form(window_forms["login"], window_forms["signup"]),
        lambda: Forms.change_form(window_forms["login"], window_forms["connectionSuccessful"]))
    window_forms["connectionSuccessful"].button_event_innit(
        lambda: Forms.change_form(window_forms["connectionSuccessful"], window_forms["selection"]),
        lambda: Forms.change_form(window_forms["connectionSuccessful"], window_forms["newStream"]))
    window_forms["selection"].button_event_innit(
        lambda: Forms.change_form(window_forms["selection"], window_forms["connectionSuccessful"]),
        lambda: Forms.change_form(window_forms["selection"], window_forms["player"]),
        window_forms["player"].set_video,
        video_play_stream)
    window_forms["emailVerify"].button_event_innit(
        lambda: Forms.change_form(window_forms["emailVerify"], window_forms["connectionSuccessful"]),
        lambda: Forms.change_form(window_forms["emailVerify"], window_forms["signup"]))
    window_forms["newStream"].button_event_innit(
        lambda: Forms.change_form(window_forms["newStream"], window_forms["connectionSuccessful"]),
        video_send_stream,
        STREAM_CLOSE_EVENT_SEND)
    window_forms["player"].button_event_innit(STREAM_CLOSE_EVENT_PLAY)


def start_ui(server_socket, aes_cypher):
    """
    A function that starts the main loop of PyGame
    :param server_socket: A socket for server communication
    :type server_socket: socket.socket
    :param aes_cypher: An object used to encrypt and decrypt messages using AES.
    :type aes_cypher: AESCypher
    :return:
    """
    global WINDOW_FORMS, STREAM_OPEN
    # set up forms
    window_forms = {
        "signup": SignUpForm(server_socket, aes_cypher),
        "login": LogInForm(server_socket, aes_cypher),
        "player": PlayerForm(server_socket, aes_cypher),
        "selection": VideoSelectionForm(server_socket, aes_cypher),
        "newStream": NewStreamForm(server_socket, aes_cypher),
        "connectionSuccessful": WatcherOrStreamerForm(),
        "emailVerify": EmailVerifyForm(server_socket, aes_cypher)}
    event_innit(window_forms)
    WINDOW_FORMS = window_forms
    # start window
    Forms.change_form(None, window_forms[FIRST_FORM])
    win = pygame.display.set_mode(window_forms[FIRST_FORM].get_size())

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                close_program(server_socket)
            elif event.type == STREAM_CLOSE_EVENT_SEND:
                while not STREAM_OPEN:
                    pass  # to handle case where client presses close button before the stream starts
                STREAM_OPEN = False
                Forms.change_form(WINDOW_FORMS["newStream"], WINDOW_FORMS["connectionSuccessful"])
            elif event.type == STREAM_CLOSE_EVENT_PLAY:
                if SOFTWARE_CLOSED:
                    exit()
                Forms.change_form(WINDOW_FORMS["player"], WINDOW_FORMS["connectionSuccessful"])
        win.fill((255, 255, 255))  # white
        Forms.update(events)
        pygame.display.update()


def main():
    """
    The main function of the program. Runs when the program starts. Initializing a secure connection with the server.
    """
    print("Connecting to server . . .")
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((SERVER_IP, SERVER_PORT))
        print("Connected!")
        print("Establishing secure connection . . .")
        message = Communication.recv_message_unsecure(server_socket)
        public_rsa_key = RSA.importKey(message["key"])
        aes_key = AESEncrypt.generate_key()
        aes_iv = AESEncrypt.generate_iv()
        rsa_cypher = PKCS1_OAEP.new(public_rsa_key)
        print(type(rsa_cypher))
        message = {"type": "aes_key", "key": aes_key, "iv": aes_iv}
        Communication.send_message_rsa(server_socket, message, rsa_cypher)
        aes_cypher = AESCypher(aes_iv, aes_key)
        
        print("Done!")
        start_ui(server_socket, aes_cypher)
    except ConnectionRefusedError:
        PopupService.error_popup("Could nor connect to server", "Could not connect to server, please try again later")


if __name__ == "__main__":
    main()
