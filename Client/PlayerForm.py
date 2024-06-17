__author__ = "Ido Senn"

from pygame_widgets.button import Button
from PygameObjects import Label, Image
import Communication
from UIConst import *


def stringify_number(num):
    """
    A function that takes a number and returns it as a shorter string
    :param num: The number to make shorter
    :type num: int
    :return: The short number
    :rtype: str
    """
    if num < 1000:
        return str(num)
    elif 1000 < num < 1000000:
        return str(round(num / 1000)) + 'K'
    else:
        return str(round(num / 1000000)) + 'M'


class PlayerForm:
    def __init__(self, server_socket, aes_cypher):
        # For communication
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
        unscaled_unlike_icon = pygame.image.load(UNLIKE_ICON)
        self.unlike_button = Button(self.win, 550, 450, 90, 40, text="0", textHAlign='right', textVAlign='centre', image=pygame.transform.scale(unscaled_unlike_icon, (25, 25)), imageHAlign='left', radius=10)
        unscaled_undislike_icon = pygame.image.load(UNDISLIKE_ICON)
        self.undislike_button = Button(self.win, 650, 450, 90, 40, text="0", textHAlign='right', textVAlign='centre', image=pygame.transform.scale(unscaled_undislike_icon, (25, 25)), imageHAlign='left', radius=10)
        self.image = Image(self.win, EMPTY_SCREEN_BYTES, 712, 400, (45, 30))
        self.close_button = Button(self.win, 550, 500, 190, 80, text="Close", font=DEFAULT_FONT_BIG, radius=10)
        self.current_reaction = 0
        self.hide()

    def show_reactions(self):
        """
        A function that shows the reactions, according to the status of the user's reaction (like, dislike...)
        """
        if self.current_reaction == 0:
            # No reaction
            self.like_button.show()
            self.dislike_button.show()
        elif self.current_reaction == 1:
            # Like
            self.unlike_button.show()
            self.dislike_button.show()
        elif self.current_reaction == -1:
            # Dislike
            self.like_button.show()
            self.undislike_button.show()

    def show(self):
        """
        Show all parts of the form
        """
        self.broadcaster_name_label.show()
        self.video_title_label.show()
        self.views_label.show()
        self.image.show()
        self.image.set_image(EMPTY_SCREEN_BYTES)
        self.close_button.show()
        self.show_reactions()

    def hide(self):
        """
        hide all parts of the form
        """
        self.broadcaster_name_label.hide()
        self.video_title_label.hide()
        self.views_label.hide()
        self.like_button.hide()
        self.dislike_button.hide()
        self.unlike_button.hide()
        self.undislike_button.hide()
        self.image.hide()
        self.close_button.hide()

    def set_video(self, video_data):
        """
        A function that sets the values of the window to a selected video
        :param video_data: Information about the video
        :type video_data: tuple
        """
        video_name, creator, views, vid, likes, dislikes, current_reaction = video_data
        self.current_reaction = current_reaction
        self.video_title_label.set_text(video_name[:16])
        self.broadcaster_name_label.set_text(creator)
        self.like_button.setText(stringify_number(likes))
        self.unlike_button.setText(stringify_number(likes))
        self.dislike_button.setText(stringify_number(dislikes))
        self.undislike_button.setText(stringify_number(dislikes))
        self.views_label.set_text(f"Views: {stringify_number(views)}")

    def like(self):
        """
        A function called when the like button is presses. changes widgets and sends data to server.
        """
        self.current_reaction = 1  # set reaction to like
        self.like_button.hide()
        self.unlike_button.show()
        self.undislike_button.hide()
        self.dislike_button.show()
        message = {"type": "reaction", "reaction": "like"}
        Communication.send_message_aes(self.server_socket, message, self.aes_cypher)

    def dislike(self):
        """
        A function called when the dislike button is presses. changes widgets and sends data to server.
        """
        self.current_reaction = -1  # set reaction to dislike
        self.dislike_button.hide()
        self.undislike_button.show()
        self.unlike_button.hide()
        self.like_button.show()
        message = {"type": "reaction", "reaction": "dislike"}
        Communication.send_message_aes(self.server_socket, message, self.aes_cypher)

    def unlike(self):
        """
        A function called when the unlike button is presses. changes widgets and sends data to server.
        """
        self.current_reaction = 0  # changes reaction to no reaction
        self.unlike_button.hide()
        self.like_button.show()
        message = {"type": "reaction", "reaction": "remove"}
        Communication.send_message_aes(self.server_socket, message, self.aes_cypher)

    def undislike(self):
        """
        A function called when the undislike button is presses. changes widgets and sends data to server.
        """
        self.current_reaction = 0  # Changes reaction to no reaction
        self.undislike_button.hide()
        self.dislike_button.show()
        message = {"type": "reaction", "reaction": "remove"}
        Communication.send_message_aes(self.server_socket, message, self.aes_cypher)

    def set_frame(self, jpeg_bytes):
        """
        Set the current image displayed on the frame
        :param jpeg_bytes: Current frame to be displayed
        :type jpeg_bytes: bytes
        """
        self.image.set_image(jpeg_bytes)

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

    def close_stream(self, close_stream_event):
        """
        A function to be called when the close button is closed (closes the stream)
        :param close_stream_event: A function that closes the stream
        :type close_stream_event: Callback
        """
        message = {"type": "close"}
        Communication.send_message_aes(self.server_socket, message, self.aes_cypher)
        pygame.event.post(pygame.event.Event(close_stream_event))

    def button_event_innit(self, close_stream_event):
        """
        A function that sets the events for all the buttons in the form
        :param close_stream_event: A function that closes the stream
        :type close_stream_event: Callback
        """
        self.like_button.setOnClick(lambda func=self.like: func())
        self.dislike_button.setOnClick(lambda func=self.dislike: func())
        self.unlike_button.setOnClick(lambda func=self.unlike: func())
        self.undislike_button.setOnClick(lambda func=self.undislike: func())
        self.close_button.setOnClick(lambda func=self.close_stream: func(close_stream_event,))

