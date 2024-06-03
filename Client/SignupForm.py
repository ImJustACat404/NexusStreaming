__author__ = "Ido Senn"

from pygame_widgets.textbox import TextBox
from pygame_widgets.button import Button
from PygameObjects import Label, Image
import Communication
from UIConst import *


def _password_edit(self):
    """
    A function that changes the values of the password input box according to input. called every edit.
    Outside the class because of a bug that prevents textbox events to be set after creation in PyGame widgets
    """
    # outside because of a bug in pygame widgets
    current_value = self.password_textbox.getText()
    if len(current_value) > len(self.password_textbox_value):
        # Added a letter
        self.password_textbox_value += current_value[len(self.password_textbox_value):]  # Add new part
        self.password_textbox.setText('*' * len(current_value))
    else:
        # Deleted a letter
        self.password_textbox_value = self.password_textbox_value[:len(current_value)]


class SignUpForm:
    def __init__(self, server_socket, aes_cypher):
        self.server_socket = server_socket
        self.aes_cypher = aes_cypher
        self.title = "Sign Up"
        self.size_x = 600
        self.size_y = 500
        self.win = pygame.display.set_mode((self.size_x, self.size_y))
        self.title_image = Image(self.win, LOGO_BYTES, 309, 159, (138, 0))
        self.email_label = Label(self.win, "E-Mail:", (100, 140), DEFAULT_FONT_SMALL, BLACK)
        self.email_textbox = TextBox(self.win, 100, 160, 400, 40, fontSize=20, borderColour=BLUE, textColour=BLACK,
                                     radius=10, borderThickness=3)
        self.password_label = Label(self.win, "Password:", (100, 220), DEFAULT_FONT_SMALL, BLACK)
        self.password_textbox = TextBox(self.win, 100, 240, 400, 40, fontSize=20, borderColour=BLUE, textColour=BLACK,
                                        radius=10, borderThickness=3, onTextChanged=_password_edit,
                                        onTextChangedParams=(self,))
        self.password_textbox_value = ""
        self.uname_label = Label(self.win, "Username:", (100, 300), DEFAULT_FONT_SMALL, BLACK)
        self.uname_textbox = TextBox(self.win, 100, 320, 400, 40, fontSize=20, borderColour=BLUE, textColour=BLACK,
                                     radius=10, borderThickness=3)

        self.sign_up_button = Button(self.win, 320, 390, 150, 30, text="sign up", radius=30, inactiveColour=BLUE,
                                     hoverColour=DARK_BLUE, pressedColour=DARKER_BLUE, textColour=WHITE,
                                     font=DEFAULT_FONT_SMALL)
        self.already_user_button = Button(self.win, 130, 390, 150, 30, text="already a user", radius=30, inactiveColour=BLUE,
                                          hoverColour=DARK_BLUE, pressedColour=DARKER_BLUE, textColour=WHITE,
                                          font=DEFAULT_FONT_SMALL)
        self.error_label = Label(self.win, "", (0, 450), DEFAULT_FONT_SMALL, RED, align="center")
        self.hide()

    def show(self):
        """
        Show all parts of the form
        """
        self.title_image.show()
        self.email_label.show()
        self.email_textbox.show()
        self.password_label.show()
        self.password_textbox.show()
        self.uname_label.show()
        self.uname_textbox.show()
        self.sign_up_button.show()
        self.already_user_button.show()
        self.error_label.show()

    def hide(self):
        """
        hide all parts of the form
        """
        self.title_image.hide()
        self.email_label.hide()
        self.email_textbox.hide()
        self.password_label.hide()
        self.password_textbox.hide()
        self.uname_label.hide()
        self.uname_textbox.hide()
        self.sign_up_button.hide()
        self.already_user_button.hide()
        self.error_label.hide()

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

    def _signup_request(self, successful_connection_callback):
        """
        A function that sends a  signup request to the server
        :param successful_connection_callback: A function to be called on a successful signup
        :type successful_connection_callback: Callback
        """
        # type="signup",  email=string, password=string, uname=string
        message = {"type": "signup", "email": self.email_textbox.getText(), "uname": self.uname_textbox.getText(),
                   "password": self.password_textbox_value}
        Communication.send_message_aes(self.server_socket, message, self.aes_cypher)
        response = Communication.recv_message_aes(self.server_socket, self.aes_cypher)
        if response["status"]:
            # sign up successful
            successful_connection_callback()
        else:
            # sign up unsuccessful
            self.error_label.set_text(response["text"])

    def button_event_innit(self, already_user_callback, successful_connection_callback):
        """
        A function that sets the events for all the buttons in the form
        :param already_user_callback: A function that switches to the login screen
        :type already_user_callback: callback
        :param successful_connection_callback: A function to be called in case of a successful signup
        :type successful_connection_callback: callback
        """
        self.already_user_button.setOnClick(already_user_callback)
        self.sign_up_button.setOnClick(lambda: self._signup_request(successful_connection_callback))
