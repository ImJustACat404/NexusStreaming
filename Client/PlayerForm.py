__author__ = "Ido Senn"

from pygame_widgets.button import Button
from PygameObjects import Label, Image
import Communication
from UIConst import *


def stringify_number(num):
    if num < 1000:
        return str(num)
    elif 1000 < num < 1000000:
        return str(num / 1000) + 'K'
    else:
        return str(num / 1000000) + 'M'


class PlayerForm:
    def __init__(self, server_socket, aes_cypher):
        self.server_socket = server_socket
        self.aes_cypher = aes_cypher
        self.title = "Video Player"
        self.size_x = 800
        self.size_y = 600
        self.win = pygame.display.set_mode((self.size_x, self.size_y))
        self.broadcaster_name_label = Label(self.win, "Broadcaster name", (50, 470), DEFAULT_FONT, BLACK)
        self.video_title_label = Label(self.win, "Video Title", (50, 510), DEFAULT_FONT, BLACK)
        self.views_label = Label(self.win, "Views: 0", (50, 550), DEFAULT_FONT, BLACK)
        unscaled_like_icon = pygame.image.load(LIKE_ICON)
        self.like_button = Button(self.win, 550, 450, 90, 40, text="0", textHAlign='right', textVAlign='centre',  image=pygame.transform.scale(unscaled_like_icon, (25, 25)), imageHAlign='left', radius=10)
        unscaled_dislike_icon = pygame.image.load(DISLIKE_ICON)
        self.dislike_button = Button(self.win, 650, 450, 90, 40, text="0", textHAlign='right', textVAlign='centre',  image=pygame.transform.scale(unscaled_dislike_icon, (25, 25)), imageHAlign='left', radius=10)
        with open(EMPTY_SCREEN, "rb") as image_file:
            jpeg_bytes = image_file.read()
        self.image = Image(self.win, jpeg_bytes, 712, 400, (45, 30))
        self.close_button = Button(self.win, 550, 500, 190, 80, text="Close", font=DEFAULT_FONT_BIG, radius=10)
        self.hide()

    def show(self):
        self.broadcaster_name_label.show()
        self.video_title_label.show()
        self.views_label.show()
        self.like_button.show()
        self.dislike_button.show()
        self.image.show()
        self.close_button.show()

    def hide(self):
        self.broadcaster_name_label.hide()
        self.video_title_label.hide()
        self.views_label.hide()
        self.like_button.hide()
        self.dislike_button.hide()
        self.image.hide()
        self.close_button.hide()

    def set_video(self, video_data):
        video_name, creator, likes, dislikes, views, _ = video_data
        self.video_title_label.set_text(video_name)
        self.broadcaster_name_label.set_text(creator)
        self.like_button.setText(stringify_number(likes))
        self.dislike_button.setText(stringify_number(dislikes))
        self.views_label.set_text(f"Views: {stringify_number(views)}")

    def like(self):
        message = {"type": "like"}
        Communication.send_message_aes(self.server_socket, message, self.aes_cypher)

    def dislike(self):
        message = {"type": "dislike"}
        Communication.send_message_aes(self.server_socket, message, self.aes_cypher)

    def set_frame(self, jpeg_bytes):
        self.image.set_image(jpeg_bytes)

    def get_size(self):
        return self.size_x, self.size_y

    def get_title(self):
        return self.title

    def close_stream(self, close_stream_event):
        message = {"type": "close"}
        Communication.send_message_aes(self.server_socket, message, self.aes_cypher)
        pygame.event.post(pygame.event.Event(close_stream_event))

    def button_event_innit(self, close_stream_event):
        self.like_button.setOnClick(lambda func=self.like: func())
        self.dislike_button.setOnClick(lambda func=self.dislike: func())
        self.close_button.setOnClick(lambda func=self.close_stream: func(close_stream_event,))

