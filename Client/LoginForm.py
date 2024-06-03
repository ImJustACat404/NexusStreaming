__author__ = "Ido Senn"

from pygame_widgets.textbox import TextBox
from pygame_widgets.button import Button
from PygameObjects import Label, Image
import Communication
from UIConst import *


def _password_edit(self):
    # outside because of a bug in pygame widgets
    current_value = self.password_textbox.getText()
    if len(current_value) > len(self.password_textbox_value):
        # Added a letter
        self.password_textbox_value += current_value[len(self.password_textbox_value):]  # Add new part
        self.password_textbox.setText('*' * len(current_value))
    else:
        # Deleted a letter
        self.password_textbox_value = self.password_textbox_value[:len(current_value)]


class LogInForm:
    def __init__(self, server_socket, aes_cypher):
        self.server_socket = server_socket
        self.aes_cypher = aes_cypher
        self.title = "Login"
        self.size_x = 600
        self.size_y = 500
        self.win = pygame.display.set_mode((self.size_x, self.size_y))
        self.title_image = Image(self.win, LOGO_BYTES, 309, 159, (138, 0))
        self.email_label = Label(self.win, "E-Mail:", (100, 140), DEFAULT_FONT_SMALL, BLACK)
        self.email_textbox = TextBox(self.win, 100, 160, 400, 40,
                                     fontSize=20,
                                     borderColour=BLUE,
                                     textColour=BLACK,
                                     radius=10,
                                     borderThickness=3)
        self.password_label = Label(self.win, "Password:", (100, 220), DEFAULT_FONT_SMALL, BLACK)
        self.password_textbox = TextBox(self.win, 100, 240, 400, 40,
                                        fontSize=20,
                                        borderColour=BLUE,
                                        textColour=BLACK,
                                        radius=10,
                                        borderThickness=3,
                                        onTextChanged=_password_edit,
                                        onTextChangedParams=(self,))
        self.password_textbox_value = ""
        self.login_button = Button(self.win, 320, 300, 150, 30,
                                   text="login",
                                   radius=30,
                                   inactiveColour=BLUE,
                                   hoverColour=DARK_BLUE,
                                   pressedColour=DARKER_BLUE,
                                   textColour=WHITE,
                                   font=DEFAULT_FONT_SMALL)
        self.new_user_button = Button(self.win, 130, 300, 150, 30,
                                      text="new user",
                                      radius=30,
                                      inactiveColour=BLUE,
                                      hoverColour=DARK_BLUE,
                                      pressedColour=DARKER_BLUE,
                                      textColour=WHITE,
                                      font=DEFAULT_FONT_SMALL)
        self.error_label = Label(self.win, "", (0, 400), DEFAULT_FONT_SMALL, RED, align="center")
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
        self.login_button.show()
        self.new_user_button.show()
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
        self.login_button.hide()
        self.new_user_button.hide()
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

    def _login_request(self, successful_connection_callback):
        """
        Send a login request to the server
        :param successful_connection_callback: A function to be called when connection is successful
        :type successful_connection_callback: callback
        """
        message = {"type": "login", "email": self.email_textbox.getText(), "password": self.password_textbox_value}
        Communication.send_message_aes(self.server_socket, message, self.aes_cypher)
        response = Communication.recv_message_aes(self.server_socket, self.aes_cypher)
        if response["status"]:
            # login successful
            successful_connection_callback()
        else:
            # login unsuccessful
            self.error_label.set_text(response["text"])

    def button_event_innit(self, new_user_callback, successful_connection_callback):
        """
        A function that sets the events for all the buttons in the form
        :param new_user_callback: A function to be called to switch to signup screen
        :type new_user_callback: Callback
        :param successful_connection_callback: A function to be called when connection is successful
        :type successful_connection_callback: Callback
        """
        self.new_user_button.setOnClick(new_user_callback)
        self.login_button.setOnClick(lambda: self._login_request(successful_connection_callback))
