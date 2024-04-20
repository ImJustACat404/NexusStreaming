from tkinter import messagebox


def error_popup(title, text):
    messagebox.showerror(title, text)


def info_popup(title, text):
    messagebox.showinfo(title, text)
