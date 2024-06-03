__author__ = "Ido Senn"

import math
import threading
from pygame_widgets.textbox import TextBox
from pygame_widgets.button import Button
from PygameObjects import Label
import Communication
from UIConst import *
import PopupService


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


class VideoSelectionForm:
    def __init__(self, server_socket, aes_cypher):
        self.server_socket = server_socket
        self.aes_cypher = aes_cypher
        self.title = "Video Selection"
        self.size_x = 800
        self.size_y = 600
        self.win = pygame.display.set_mode((self.size_x, self.size_y))
        self.search_bar = TextBox(self.win, 5, 5, 700, 50, borderColour=BLUE, radius=10, fontSize=30)
        unscaled_search_icon = pygame.image.load(SEARCH_ICON)
        self.search_button = Button(self.win, 710, 5, 85, 50, colour=BLUE, radius=10, hoverColour=DARK_BLUE, pressedColour=DARKER_BLUE, image=pygame.transform.scale(unscaled_search_icon, (30, 30)))
        video1 = Button(self.win, 15, 80, 250, 140, radius=15, colour=LIGHT_BLUE)
        text1 = Label(self.win, "", (video1.getX() + 5, video1.getY() + 5), DEFAULT_FONT_SMALL, WHITE)
        video2 = Button(self.win, 275, 80, 250, 140, radius=15, colour=LIGHT_BLUE)
        text2 = Label(self.win, "", (video2.getX() + 5, video2.getY() + 5), DEFAULT_FONT_SMALL, WHITE)
        video3 = Button(self.win, 535, 80, 250, 140, radius=15, colour=LIGHT_BLUE)
        text3 = Label(self.win, "", (video3.getX() + 5, video3.getY() + 5), DEFAULT_FONT_SMALL, WHITE)
        video4 = Button(self.win, 15, 230, 250, 140, radius=15, colour=LIGHT_BLUE)
        text4 = Label(self.win, "", (video4.getX() + 5, video4.getY() + 5), DEFAULT_FONT_SMALL, WHITE)
        video5 = Button(self.win, 275, 230, 250, 140, radius=15, colour=LIGHT_BLUE)
        text5 = Label(self.win, "", (video5.getX() + 5, video5.getY() + 5), DEFAULT_FONT_SMALL, WHITE)
        video6 = Button(self.win, 535, 230, 250, 140, radius=15, colour=LIGHT_BLUE)
        text6 = Label(self.win, "", (video6.getX() + 5, video6.getY() + 5), DEFAULT_FONT_SMALL, WHITE)
        video7 = Button(self.win, 15, 380, 250, 140, radius=15, colour=LIGHT_BLUE)
        text7 = Label(self.win, "", (video7.getX() + 5, video7.getY() + 5), DEFAULT_FONT_SMALL, WHITE)
        video8 = Button(self.win, 275, 380, 250, 140, radius=15, colour=LIGHT_BLUE)
        text8 = Label(self.win, "", (video8.getX() + 5, video8.getY() + 5), DEFAULT_FONT_SMALL, WHITE)
        video9 = Button(self.win, 535, 380, 250, 140, radius=15, colour=LIGHT_BLUE)
        text9 = Label(self.win, "", (video9.getX() + 5, video9.getY() + 5), DEFAULT_FONT_SMALL, WHITE)
        self.video_frames = [(video1, text1), (video2, text2), (video3, text3), (video4, text4), (video5, text5), (video6, text6), (video7, text7), (video8, text8), (video9, text9)]
        unscaled_next_icon = pygame.image.load(NEXT_ICON)
        self.next_button = Button(self.win, 430, 540, 80, 40, image=pygame.transform.scale(unscaled_next_icon, (30, 30)), colour=BLUE, radius=10, hoverColour=DARK_BLUE, pressedColour=DARKER_BLUE)
        unscaled_prev_icon = pygame.image.load(PREV_ICON)
        self.previous_button = Button(self.win, 290, 540, 80, 40, image=pygame.transform.scale(unscaled_prev_icon, (30, 30)), colour=BLUE, radius=10, hoverColour=DARK_BLUE, pressedColour=DARKER_BLUE)
        unscaled_back_icon = pygame.image.load(BACK_ICON)
        self.back_button = Button(self.win, 20, 540, 80, 40, image=pygame.transform.scale(unscaled_back_icon, (30, 30)), colour=BLUE, radius=10, hoverColour=DARK_BLUE, pressedColour=DARKER_BLUE)
        self.video_list = []
        self.current_page = 0
        self.hide()

    def update_tiles(self):
        """
        A function that updates the update of the stream tiles on the screen
        """
        video_index = self.current_page * 9  # set as the first video
        for frame in self.video_frames:
            if video_index < len(self.video_list):  # for case where the page isn't full
                frame[0].show()
                frame[1].show()
                frame[1].set_text(f"\n  {self.video_list[video_index][0][:16]}\n"
                                  f"     Creator: {self.video_list[video_index][1]}\n"
                                  f"     Views: {stringify_number(self.video_list[video_index][2])}\n"
                                  f"     Likes: {stringify_number(self.video_list[video_index][4])}"
                                  f"  Dislikes: {stringify_number(self.video_list[video_index][5])}")
            else:
                # frame not used
                frame[0].hide()
                frame[1].hide()
            video_index += 1
        last_page = math.ceil(len(self.video_list) / 9) - 1
        # Show and hide next and previous buttons
        if self.current_page > 0:
            self.previous_button.show()
        else:
            self.previous_button.hide()
        if self.current_page < last_page:
            self.next_button.show()
        else:
            self.next_button.hide()

    def search(self):
        """
        A function that send a search request to the server and updates the screen accordingly
        """
        keyword = self.search_bar.getText()
        message = {"type": "search", "keyword": keyword}
        Communication.send_message_aes(self.server_socket, message, self.aes_cypher)
        response = Communication.recv_message_aes(self.server_socket, self.aes_cypher)
        self.video_list = response["results"]
        self.current_page = 0
        self.update_tiles()

    def watch_video(self, button_index, switch_to_player_callback, set_video_callback, start_video_watch_callback):
        """
        A function called when the user wants to watch a video
        :param button_index: Index of the tile the user presses (from 1 to 9)
        :type button_index: int
        :param switch_to_player_callback: A function that switches to the player form
        :type switch_to_player_callback: Callback
        :param set_video_callback: A function that sets the video data on the player form
        :type set_video_callback: callback
        :param start_video_watch_callback: A function that starts plays the stream data from the server
        :type start_video_watch_callback: callback
        """
        selected_video = self.video_list[self.current_page * 9 + button_index]  # get video index
        message = {"type": "watch", "vid": selected_video[3]}  # send watch request to server
        Communication.send_message_aes(self.server_socket, message, self.aes_cypher)
        response = Communication.recv_message_aes(self.server_socket, self.aes_cypher)
        if response["status"]:
            # video is available
            set_video_callback(selected_video)
            threading.Thread(target=start_video_watch_callback, args=(self.server_socket, self.aes_cypher)).start()
            switch_to_player_callback()
        else:
            PopupService.error_popup("Error while trying to connect to stream", response["text"])

    def next(self):
        """
        A function that moves to the next results page
        """
        self.current_page += 1
        self.update_tiles()

    def previous(self):
        """
        A function that moves to the previous results page
        """
        self.current_page -= 1
        self.update_tiles()

    def show(self):
        """
        Show all parts of the form
        """
        self.search()
        self.update_tiles()
        self.search_bar.show()
        self.search_button.show()
        self.back_button.show()

    def hide(self):
        """
        hide all parts of the form
        """
        for frame in self.video_frames:
            frame[0].hide()
            frame[1].hide()
        self.search_bar.hide()
        self.search_button.hide()
        self.previous_button.hide()
        self.next_button.hide()
        self.back_button.hide()

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

    def button_event_innit(self, return_to_menu_callback, switch_to_player_callback, set_video_callback, start_video_watch_callback):
        """
        A function that sets the events for all the buttons in the form
        :param return_to_menu_callback: A function that switches to the main menu form
        :type return_to_menu_callback: callback
        :param switch_to_player_callback: A function that switches to the player form
        :type switch_to_player_callback: callback
        :param set_video_callback: A function that sets the video data on the player form
        :type set_video_callback: callback
        :param start_video_watch_callback: A function that starts playing the stream
        :type start_video_watch_callback: callback
        """
        # written like that so the functions won't be called on definition
        self.search_button.setOnClick(lambda func=self.search: func())
        self.next_button.setOnClick(lambda func=self.next: func())
        self.previous_button.setOnClick(lambda func=self.previous: func())
        self.back_button.setOnClick(return_to_menu_callback)
        index = 0
        for frame in self.video_frames:
            frame[0].setOnClick(lambda i=index: self.watch_video(i, switch_to_player_callback, set_video_callback, start_video_watch_callback))
            index += 1
