__author__ = "Ido Senn"

from pygame_widgets.button import Button
from UIConst import *


class WatcherOrStreamerForm:
    def __init__(self):
        self.title = "Select action"
        self.size_x = 600
        self.size_y = 500
        self.win = pygame.display.set_mode((self.size_x, self.size_y))
        self.new_stream_button = Button(self.win, 125, 75, 350, 150, text="Create new stream", colour=BLUE, radius=10, hoverColour=DARK_BLUE, pressedColour=DARKER_BLUE, font=DEFAULT_FONT, textColour=WHITE)
        self.watch_button = Button(self.win, 125, 275, 350, 150, text="Watch existing streams", colour=BLUE, radius=10, hoverColour=DARK_BLUE, pressedColour=DARKER_BLUE, font=DEFAULT_FONT, textColour=WHITE)
        self.hide()

    def show(self):
        self.new_stream_button.show()
        self.watch_button.show()

    def hide(self):
        self.new_stream_button.hide()
        self.watch_button.hide()

    def get_size(self):
        return self.size_x, self.size_y

    def get_title(self):
        return self.title

    def button_event_innit(self, watch_callback, stream_callback):
        self.new_stream_button.setOnClick(stream_callback)
        self.watch_button.setOnClick(watch_callback)
