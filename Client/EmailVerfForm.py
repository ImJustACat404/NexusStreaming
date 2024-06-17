__author__ = "Ido Senn"

from pygame_widgets.textbox import TextBox
from pygame_widgets.button import Button
from PygameObjects import Label
import Communication
from UIConst import *
import PopupService


class EmailVerifyForm:
    def __init__(self, server_socket, aes_cypher):
        self.server_socket = server_socket
        self.aes_cypher = aes_cypher
        self.title = "Verify Email"
        self.size_x = 600
        self.size_y = 500
        self.win = pygame.display.set_mode((self.size_x, self.size_y))

        self.main_label = Label(
            self.win,
            "A code was sent to your email address. Please enter it here:",
            (0, 150),
            DEFAULT_FONT_SMALL,
            BLACK,
            "center"
        )
        self.code_textbox = TextBox(
            self.win,
            250,
            200,
            100,
            50,
            borderColour=BLUE,
            textColour=BLACK,
            radius=10,
            borderThickness=3
        )
        self.verify_button = Button(
            self.win,
            200,
            300,
            200,
            50,
            text="Verify",
            font=DEFAULT_FONT_SMALL,
            radius=30,
            inactiveColour=BLUE,
            hoverColour=DARK_BLUE,
            pressedColour=DARKER_BLUE,
            textColour=WHITE
        )
        self.hide()

    def show(self):
        """
        Show all parts of the form
        """
        self.main_label.show()
        self.code_textbox.show()
        self.verify_button.show()

    def hide(self):
        """
        hide all parts of the form
        """
        self.main_label.hide()
        self.code_textbox.hide()
        self.verify_button.hide()

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

    def verify_button_press(self, unsuccessful_callback, successful_callback):
        """
        A function called when the "verify" button is pressed
        :param unsuccessful_callback: A callback to a function to be called when connection is unsuccessful
        :type unsuccessful_callback: callback
        :param successful_callback: A callback to a function to be called when connection is successful
        :type successful_callback: callback
        """
        code = self.code_textbox.getText()
        message = {"type": "code", "code": code}
        Communication.send_message_aes(self.server_socket, message, self.aes_cypher)
        response = Communication.recv_message_aes(self.server_socket, self.aes_cypher)
        if response["status"]:
            successful_callback()
        else:
            PopupService.error_popup("Verification failed!", response["text"])
            unsuccessful_callback()

    def button_event_innit(self, successful_callback, unsuccessful_callback):
        """
        A function that sets the events for all the buttons in the form
        :param unsuccessful_callback: A callback to a function to be called when connection is unsuccessful
        :type unsuccessful_callback: callback
        :param successful_callback: A callback to a function to be called when connection is successful
        :type successful_callback: callback
        """
        self.verify_button.setOnClick(lambda: self.verify_button_press(unsuccessful_callback, successful_callback))
