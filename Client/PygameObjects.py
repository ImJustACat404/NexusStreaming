__author__ = "Ido Senn"

import pygame
import io


class Label:
    instances = []

    def __init__(self, surface, text, pos, font, color=(0, 0, 0), align="left"):
        self.surface = surface
        self.text = text
        self.pos = pos
        self.font = font
        self.color = color
        self.shown = True
        self.align = align
        Label.instances.append(self)

    def print_to_surface(self):
        """
        A function that prints the label to the given surface
        """
        words = [word.split(' ') for word in self.text.splitlines()]  # 2D array where each row is a list of words.
        space = self.font.size(' ')[0]  # The width of a space.
        max_width, max_height = self.surface.get_size()
        x, y = self.pos
        for line in words:
            printed_length = 0  # The length of the text already printed to the screen
            line_width, _ = self.font.render(' '.join(line), True, self.color).get_size()  # get width of the current line
            if self.align == "center":
                # center text to screen
                if x + (line_width / 2) < max_width:  # If line isn't too wide
                    x = (max_width - line_width) / 2 + self.pos[0]  # set text x position accordingly
            for word in line:
                word_surface = self.font.render(word, True, self.color)  # render every word
                word_width, word_height = word_surface.get_size()  # get word dimensions on screen
                if x + word_width >= max_width:
                    # id reached line end, start now line
                    # Reset the x.
                    x = self.pos[0]
                    y += word_height  # Start on new row.
                self.surface.blit(word_surface, (x, y))  # show rendered word on the screen
                x += word_width + space  # add space width to x value
                printed_length += word_width + space  # add current word with to total line width
            # reached line end
            x = self.pos[0]  # Reset the x.
            y += word_height  # Start on new row.

    def show(self):
        """
        show widget on screen
        """
        self.shown = True

    def hide(self):
        """
        Hide widget
        """
        self.shown = False

    def set_text(self, text):
        """
        Set label text
        :param text: New text
        :type text: str
        """
        self.text = text

    @staticmethod
    def update():
        """
        A function that prints to the screen all Labels set to "shown"
        """
        for label in Label.instances:
            if label.shown:
                label.print_to_surface()


class Image:
    instances = []

    def __init__(self, surface, jpeg_bytes, width, height, pos):
        self.surface = surface
        self.width = width
        self.height = height
        bytes_io = io.BytesIO(jpeg_bytes)
        unscaled_image = pygame.image.load(bytes_io)
        self.image = pygame.transform.scale(unscaled_image, (self.width, self.height))
        self.pos = pos
        self.shown = True
        Image.instances.append(self)

    def print_to_surface(self):
        """
        A function that prints the image on the screen
        """
        self.surface.blit(self.image, self.pos)

    def show(self):
        """
        show widget on screen
        """
        self.shown = True

    def hide(self):
        """
        hide widget
        """
        self.shown = False

    def set_image(self, jpeg_bytes):
        """
        A function that sets a new value to the image
        :param jpeg_bytes: Bytes of a jpeg image
        :type jpeg_bytes: bytes
        """
        bytes_io = io.BytesIO(jpeg_bytes)
        unscaled_image = pygame.image.load(bytes_io)
        self.image = pygame.transform.scale(unscaled_image, (self.width, self.height))

    def get_image(self):
        """
        A function that returns the current image shown on the screen in jpeg bytes.
        :return: Current image
        :rtype: bytes
        """
        return self.image

    @staticmethod
    def update():
        """
        A function that prints to the screen all Images set to "shown"
        """
        for current_image in Image.instances:
            if current_image.shown:
                current_image.print_to_surface()


def update():
    """
    Update all widgets
    """
    Label.update()
    Image.update()
