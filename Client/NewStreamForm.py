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
        self.window_title = Label(self.win, "New Stream", (0, 50), DEFAULT_FONT_BIG, BLUE, align="center")
        self.title_label = Label(self.win, "Title:", (100, 150), DEFAULT_FONT, BLUE)
        self.title_textbox = TextBox(self.win, 200, 135, 400, 50, radius=10, borderColour=BLUE)
        self.capture_label = Label(self.win, "Capture mode:", (100, 250), DEFAULT_FONT, BLUE)
        self.capture_dropdown = Dropdown(self.win, 300, 230, 200, 50, "Select device", ["Camera", "Screen"], font=DEFAULT_FONT_SMALL, borderRadius=10, textColour=RED)
        self.start_button = Button(self.win, 250, 400, 300, 100, text="start", textColour=BLUE, font=DEFAULT_FONT_BIG, radius=10)
        self.stop_button = Button(self.win, 250, 400, 300, 100, text="stop", textColour=RED, font=DEFAULT_FONT_BIG, radius=10)
        self.hide()

    def show(self):
        self.window_title.show()
        self.title_label.show()
        self.title_textbox.show()
        self.capture_label.show()
        self.capture_dropdown.show()
        self.start_button.show()

    def hide(self):
        self.window_title.hide()
        self.title_label.hide()
        self.title_textbox.hide()
        self.capture_label.hide()
        self.capture_dropdown.hide()
        self.start_button.hide()
        self.stop_button.hide()

    def get_size(self):
        return self.size_x, self.size_y

    def get_title(self):
        return self.title

    def start_button_press(self, stream_start_event):
        self.start_button.hide()
        message = {"type": "broadcast", "title": self.title_textbox.getText()}
        Communication.send_message_aes(self.server_socket, message, self.aes_cypher)
        threading.Thread(target=stream_start_event, args=(self.server_socket, self.aes_cypher,  self.capture_dropdown.getSelected() == "Screen")).start()
        self.stop_button.show()

    def stop_button_press(self, stream_stop_event):
        self.stop_button.hide()
        stream_stop_event()

    def button_event_innit(self, stream_start_event, stream_stop_event):
        self.stop_button.setOnClick(lambda func=self.stop_button_press: func(stream_stop_event))
        self.start_button.setOnClick(lambda func=self.start_button_press: func(stream_start_event))
