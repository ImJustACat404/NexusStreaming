from tkinter import messagebox


def error_popup(title, text):
    """
    Shows an error popup to the user
    :param title: Popup title
    :type title: str
    :param text: The text on the popup
    :type text: str
    """
    messagebox.showerror(title, text)


def info_popup(title, text):
    """
    Shows an info popup to the user
    :param title: Popup title
    :type title: str
    :param text: The text on the popup
    :type text: str
    """
    messagebox.showinfo(title, text)
