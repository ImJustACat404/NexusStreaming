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
import PopupService
pygame.init()


# Communication constants
SERVER_IP = "127.0.0.1"
SERVER_PORT = 8001

# Form globals
FIRST_FORM = "login"  # This is the first form to be displayed when starting Nexus
WINDOW_FORMS = {}
STREAM_OPEN = False
SOFTWARE_CLOSED = False
STREAM_CLOSE_EVENT_PLAY = pygame.USEREVENT + 1
STREAM_CLOSE_EVENT_SEND = pygame.USEREVENT + 2


def close_program(server_socket):
    """
    A function called when the program is being closed
    """
    global STREAM_OPEN, SOFTWARE_CLOSED
    # Set program as closed (used by other threads)
    SOFTWARE_CLOSED = True
    # Close currently open streams
    STREAM_OPEN = False
    # Close socket
    server_socket.close()
    # Close pygame
    pygame.quit()
    # close program
    quit()


def video_send_stream(server_socket, aes_cypher, is_screen):
    """
    Sharing video and audio with the server
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
    audio_stream = None
    try:
        if is_screen:
            # User selected screen sharing
            vid_stream = ImageStream.ScreenStream()
        else:
            # User selected camera sharing
            vid_stream = ImageStream.CameraStream()
        # Create audio input stream
        audio_stream = AudioRecord.AudioStream()
        STREAM_OPEN = True  # Set program to stream mode
        try:
            while STREAM_OPEN:  # closes when user presses stop
                # send image data to server
                video_msg = {"type": "frame", "data": vid_stream.get_current_frame()}
                Communication.send_message_aes(server_socket, video_msg, aes_cypher)
                # send audio data to server
                audio_msg = {"type": "audio", "data": audio_stream.get_current_audio()}
                Communication.send_message_aes(server_socket, audio_msg, aes_cypher)
            # stream closed
            Communication.send_message_aes(server_socket, {"type": "close"}, aes_cypher)  # notify server
            audio_stream.terminate()  # close audio stream
        except OSError:
            # socket was closed
            audio_stream.terminate()
        except Exception as e:
            # Hardware error, lost access to camera or mic while in stream
            print(f"Could not access hardware! Error: {e}")
            Communication.send_message_aes(server_socket, {"type": "close"}, aes_cypher)  # notify server
            if audio_stream is not None:  # close audio stream if there is one
                audio_stream.terminate()
            # call send stream close event (changes screens)
            pygame.event.post(pygame.event.Event(STREAM_CLOSE_EVENT_SEND))
            # notify user
            PopupService.error_popup("Hardware Error",
                                     "Could not connect to hardware devices!\n"
                                     "Make sure that a microphone and camera are connected and try again!")
    except Exception as e:
        # Hardware error, lost access before connecting to stream
        print(f"Could not access hardware! Error: {e}")
        Communication.send_message_aes(server_socket, {"type": "close"}, aes_cypher)
        pygame.event.post(pygame.event.Event(STREAM_CLOSE_EVENT_SEND))  # call send stream close event (changes screens)
        STREAM_OPEN = True  # Set program to stream mode to deal with socket - emptying mechanism
        if audio_stream is not None:  # close audio stream if there is one
            audio_stream.terminate()
        # notify user
        PopupService.error_popup("Hardware Error",
                                 "Could not connect to hardware devices!\n"
                                 "Make sure that a microphone and camera are connected and try again!")


def video_play_stream(server_socket, aes_cypher):
    """
    Playing video and audio from server
    :param server_socket: socket for server communications
    :type server_socket: socket.socket
    :param aes_cypher: An object used to encrypt and decrypt data using AES
    :type aes_cypher: AESCypher
    """
    global STREAM_OPEN
    audio_stream = None
    try:
        audio_stream = AudioPlay.AudioStream()
    except Exception as e:
        # no audio output device connected
        print(f"Could not access hardware! Error: {e}")
        message = {"type": "close"}  # notify server
        Communication.send_message_aes(server_socket, message, aes_cypher)
        # notify user
        PopupService.error_popup("Hardware Error",
                                 "Could not connect to hardware devices!\n"
                                 "Make sure that a microphone and camera are connected and try again!")
    STREAM_OPEN = True  # set program to stream mode
    while STREAM_OPEN:  # while user didn't close stream
        message = Communication.recv_message_aes(server_socket, aes_cypher)  # recv stream piece
        if message["type"] == "close":
            # if stream closed (server side), quit loop
            STREAM_OPEN = False
            break
        elif message["type"] == "audio":
            # data is audio
            try:
                audio_stream.play_audio(message["data"])
            except Exception as e:
                # Speaker disconnected while playing
                print(f"Could not access hardware! Error: {e}")
                message = {"type": "close"}  # notify server
                Communication.send_message_aes(server_socket, message, aes_cypher)
                message = Communication.recv_message_aes(server_socket, aes_cypher)
                while message["type"] != "close":
                    # empty socket
                    message = Communication.recv_message_aes(server_socket, aes_cypher)
                STREAM_OPEN = False  # close stream
        elif message["type"] == "frame":
            # data is an image
            WINDOW_FORMS["player"].set_frame(message["data"])  # send to UI
    audio_stream.terminate()  # close audio stream
    pygame.event.post(pygame.event.Event(STREAM_CLOSE_EVENT_PLAY))  # call stream playing close event (change window)


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
                # pressed window 'x'
                close_program(server_socket)
            elif event.type == STREAM_CLOSE_EVENT_SEND:
                # closed stream sending
                while not STREAM_OPEN:
                    pass  # to handle case where client presses close button before the stream starts
                STREAM_OPEN = False  # set stream mode to false
                Forms.change_form(WINDOW_FORMS["newStream"], WINDOW_FORMS["connectionSuccessful"])
            elif event.type == STREAM_CLOSE_EVENT_PLAY:
                # closed stream playing
                if SOFTWARE_CLOSED:
                    # handle case where the stream closed because the program closed
                    exit()
                Forms.change_form(WINDOW_FORMS["player"], WINDOW_FORMS["connectionSuccessful"])
        win.fill((255, 255, 255))  # white background
        Forms.update(events)  # update all window forms
        pygame.display.update()  # update display


def main():
    """
    The main function of the program. Runs when the program starts. Initializing a secure connection with the server.
    """
    print("Connecting to server . . .")
    try:
        # distribute AES key with RSA
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((SERVER_IP, SERVER_PORT))
        print("Connected!")
        print("Establishing secure connection . . .")
        message = Communication.recv_message_unsecure(server_socket)
        public_rsa_key = message["key"]
        aes_key = AESEncrypt.generate_key()
        aes_iv = AESEncrypt.generate_iv()
        message = {"type": "aes_key", "key": aes_key, "iv": aes_iv}
        Communication.send_message_rsa(server_socket, message, public_rsa_key)
        aes_cypher = AESCypher(aes_iv, aes_key)
        
        print("Done!")
        start_ui(server_socket, aes_cypher)
    except (ConnectionRefusedError, WindowsError):
        # Server down
        PopupService.error_popup("Could nor connect to server", "Could not connect to server, please try again later")
    except Exception as error:
        # error I did not encounter
        PopupService.error_popup("Fatal Error!", f"Fatal error!\n{error}")


if __name__ == "__main__":
    main()
