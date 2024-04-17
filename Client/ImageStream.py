__author__ = "Ido Senn"

import cv2
import pyautogui
import numpy as np


DEFAULT_RES = (427, 240)
BORDER_COLOR = (0, 0, 0)


def adjust_frame(frame, ratio):
    if round(ratio, 2) == round(16 / 9, 2):
        frame = cv2.resize(frame, DEFAULT_RES)
    elif ratio < (16 / 9):
        width = int(DEFAULT_RES[1] * ratio)
        frame = cv2.resize(frame, (width, DEFAULT_RES[1]))
        border_width_left = int((DEFAULT_RES[0] - width) / 2)
        border_width_right = (DEFAULT_RES[0] - width) - border_width_left
        frame = cv2.copyMakeBorder(frame, 0, 0, border_width_left, border_width_right, cv2.BORDER_CONSTANT,
                                   value=BORDER_COLOR)
    elif ratio > (16 / 9):
        height = int(DEFAULT_RES[0] / ratio)
        frame = cv2.resize(frame, (DEFAULT_RES[0], height))
        border_width_up = int((DEFAULT_RES[1] - height) / 2)
        border_width_down = (DEFAULT_RES[1] - height) - border_width_up
        frame = cv2.copyMakeBorder(frame, border_width_up, border_width_down, 0, 0, cv2.BORDER_CONSTANT,
                                   value=BORDER_COLOR)
    return frame


class CameraStream:
    def __init__(self):
        self.capture = cv2.VideoCapture(0)
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        camera_height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        camera_width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.ratio = camera_width / camera_height

    def get_current_frame(self):
        """
        A function that returns the current frame from the camera in .jpg format
        :return: current frame
        :rtype: bytes
        """
        # Get current frame
        ret, frame = self.capture.read()  # object type of frame is 'numpy.ndarray'
        # Resize Frame
        frame = adjust_frame(frame, self.ratio)
        # Convert to .jpg format
        _, jpeg_binary = cv2.imencode('.jpg', frame)  # Encode the frame as JPEG
        jpeg_bytes = jpeg_binary.tobytes()  # Convert to JPEG binary
        return jpeg_bytes


class ScreenStream:
    def __init__(self):
        # Get the screen resolution
        screen_width, screen_height = pyautogui.size()
        self.ratio = screen_width / screen_height

    def get_current_frame(self):
        """
        A function that returns the current frame from the screen in .jpg format
        :return: current frame
        :rtype: bytes
        """
        # Get current frame
        screen = pyautogui.screenshot()
        # Convert the screenshot to an OpenCV image
        # This is done by converting the PIL Image to a numpy array
        # and then converting the color format from RGB to BGR (which is the format that OpenCV uses)
        frame = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
        # Resize Frame
        frame = adjust_frame(frame, self.ratio)
        # Convert to .jpg format
        _, jpeg_binary = cv2.imencode('.jpg', frame)  # Encode the frame as JPEG
        jpeg_bytes = jpeg_binary.tobytes()  # Convert to JPEG binary
        return jpeg_bytes
