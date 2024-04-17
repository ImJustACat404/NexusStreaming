__author__ = "Ido Senn"

import pygame_widgets
import PygameObjects
from UIConst import *
pygame.init()


def update(events):
    pygame_widgets.update(events)
    PygameObjects.update()


def change_form(current, new):
    if current is not None:
        current.hide()
    new.show()
    pygame.display.set_mode(new.get_size())  # sometimes causes flickering
    pygame.display.set_caption(new.get_title())
    pygame.display.set_icon(pygame.image.load(LOGO_SMALL))

