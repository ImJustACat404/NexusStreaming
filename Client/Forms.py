__author__ = "Ido Senn"

import pygame_widgets
import PygameObjects
from UIConst import *
pygame.init()


def update(events):
    """
    A function that updated the UI, by sending the events to all UI widget moduls
    :param events: A list of pygame events, that recently occurred
    :type events: list
    """
    pygame_widgets.update(events)
    PygameObjects.update()


def change_form(current, new):
    """
    A function that switches between forms
    :param current: The form currently displayed
    :type current: Form
    :param new: The new form to be displayed
    :type new: Form
    """
    if current is not None:  # None if it's the first form
        current.hide()
    new.show()
    pygame.display.set_mode(new.get_size())  # sometimes causes flickering
    pygame.display.set_caption(new.get_title())
    pygame.display.set_icon(pygame.image.load(LOGO_SMALL))

