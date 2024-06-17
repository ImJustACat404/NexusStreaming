__author__ = "Ido Senn"

import threading
from pygame_widgets.textbox import TextBox
from pygame_widgets.button import Button
from PygameObjects import Label
from pygame_widgets.dropdown import Dropdown
import Communication
from UIConst import *


class NewStreamForm:
    def __init__(self, server_socket, aes_cypher):
        self.server_socket = server_socket
        self.aes_cypher = aes_cypher
        self.title = "New stream"
        self.size_x = 800
        self.size_y = 600
        self.win = pygame.display.set_mode((self.size_x, self.size_y))
        self.window_title = Label(
            self.win,
            "New Stream",
            (0, 50),
            DEFAULT_FONT_BIG,
            BLUE, align="center"
        )
        self.live_label = Label(
            self.win,
            "Now live!",
            (0, 50),
            DEFAULT_FONT_BIG,
            BLUE,
            align="center"
        )
        self.title_label = Label(
            self.win,
            "Title:",
            (100, 150),
            DEFAULT_FONT,
            BLUE
        )
        self.title_textbox = TextBox(
            self.win,
            200,
            135,
            400,
            50,
            radius=10,
            borderColour=BLUE
        )
        self.capture_label = Label(
            self.win,
            "Capture mode:",
            (100, 250),
            DEFAULT_FONT,
            BLUE
        )
        self.capture_dropdown = Dropdown(
            self.win,
            300,
            230,
            200,
            50,
            "Select device",
            ["Camera", "Screen"],
            font=DEFAULT_FONT_SMALL,
            borderRadius=10,
            textColour=RED
        )
        self.start_button = Button(
            self.win,
            250,
            400,
            300,
            100,
            text="start",
            textColour=BLUE,
            font=DEFAULT_FONT_BIG,
            radius=10
        )

        self.closing_message = Label(
            self.win,
            "Closing...",
            (0, 400),
            DEFAULT_FONT_BIG,
            BLUE,
            align="center"
        )
        self.stop_button = Button(
            self.win,
            250,
            400,
            300,
            100,
            text="stop",
            textColour=RED,
            font=DEFAULT_FONT_BIG,
            radius=10
        )
        unscaled_back_icon = pygame.image.load(BACK_ICON)
        self.back_button = Button(
            self.win,
            20,
            540,
            80,
            40,
            image=pygame.transform.scale(unscaled_back_icon, (30, 30)),
            colour=BLUE,
            radius=10,
            hoverColour=DARK_BLUE,
            pressedColour=DARKER_BLUE
        )
        self.hide()

    def show(self):
        """
        Show all form components
        """
        self.window_title.show()
        self.title_label.show()
        self.title_textbox.show()
        self.capture_label.show()
        self.capture_dropdown.show()
        self.start_button.show()
        self.back_button.show()

    def hide(self):
        """
        Hide all form components
        """
        self.window_title.hide()
        self.title_label.hide()
        self.title_textbox.hide()
        self.capture_label.hide()
        self.capture_dropdown.hide()
        self.start_button.hide()
        self.stop_button.hide()
        self.back_button.hide()
        self.closing_message.hide()
        self.live_label.hide()

    def get_size(self):
        """
        Get size of the form window
        :return: size of the screen
        :rtype: tuple
        """
        return self.size_x, self.size_y

    def get_title(self):
        """
        Get the title of the Form
        :return: Form title
        :rtype: string
        """
        return self.title

    def start_button_press(self, stream_start_callback):
        """
        A function to be called when the start button is pressed
        :param stream_start_callback: A function that starts the stream
        :type stream_start_callback: Callback
        """
        self.start_button.hide()
        self.back_button.hide()
        self.window_title.hide()
        self.title_label.hide()
        self.title_textbox.hide()
        self.capture_label.hide()
        self.capture_dropdown.hide()

        message = {"type": "broadcast", "title": self.title_textbox.getText()}
        Communication.send_message_aes(self.server_socket, message, self.aes_cypher)
        threading.Thread(
            target=stream_start_callback,
            args=(self.server_socket, self.aes_cypher,  self.capture_dropdown.getSelected() == "Screen")
        ).start()
        self.stop_button.show()
        self.live_label.show()

    def stop_button_press(self, stream_stop_event):
        """
        A function called when the stop button is pressed
        :param stream_stop_event: A function that stops a running event
        :type stream_stop_event: Callback
        """
        self.stop_button.hide()
        self.closing_message.show()
        pygame.event.post(pygame.event.Event(stream_stop_event))

    def button_event_innit(self, return_to_menu_callback, stream_start_callback, stream_stop_event):
        """
        A function that sets the events for all the buttons in the form
        :param return_to_menu_callback: A function to be called to return to the main menu
        :type return_to_menu_callback: Callback
        :param stream_start_callback: A function to be called to start a stream
        :type stream_start_callback: Callback
        :param stream_stop_event: A PyGame event to be called to stop the stream
        :type stream_stop_event: PyGame event
        """
        self.stop_button.setOnClick(lambda func=self.stop_button_press: func(stream_stop_event))
        self.start_button.setOnClick(lambda func=self.start_button_press: func(stream_start_callback))
        self.back_button.setOnClick(return_to_menu_callback)
