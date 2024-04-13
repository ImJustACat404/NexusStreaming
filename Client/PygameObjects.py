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
        words = [word.split(' ') for word in self.text.splitlines()]  # 2D array where each row is a list of words.
        space = self.font.size(' ')[0]  # The width of a space.
        max_width, max_height = self.surface.get_size()
        x, y = self.pos
        for line in words:
            printed_length = 0
            line_width, _ = self.font.render(' '.join(line), True, self.color).get_size()
            if self.align == "center":
                if x + (line_width / 2) < max_width:
                    x = (max_width - line_width) / 2 + self.pos[0]
            for word in line:
                word_surface = self.font.render(word, True, self.color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width:
                    # Reset the x.
                    x = self.pos[0]
                   # if self.align == "center":
                        #if (line_width - printed_length) < max_width:
                           # x = (max_width - line_width) / 2 + self.pos[0]
                    #else:
                        #x = self.pos[0]
                    y += word_height  # Start on new row.
                self.surface.blit(word_surface, (x, y))
                x += word_width + space
                printed_length += word_width + space
            x = self.pos[0]  # Reset the x.
            y += word_height  # Start on new row.

    def show(self):
        self.shown = True

    def hide(self):
        self.shown = False

    def set_text(self, text):
        self.text = text

    @staticmethod
    def update():
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
        self.surface.blit(self.image, self.pos)

    def show(self):
        self.shown = True

    def hide(self):
        self.shown = False

    def set_image(self, jpeg_bytes):
        bytes_io = io.BytesIO(jpeg_bytes)
        unscaled_image = pygame.image.load(bytes_io)
        self.image = pygame.transform.scale(unscaled_image, (self.width, self.height))

    def get_image(self):
        return self.image

    @staticmethod
    def update():
        for current_image in Image.instances:
            if current_image.shown:
                current_image.print_to_surface()


def update():
    Label.update()
    Image.update()
