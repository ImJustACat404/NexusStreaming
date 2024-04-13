import tkinter as tk
from tkinter.constants import *
from time import perf_counter as cur_time


LONG_CLICK = 2.0  # Seconds.
start_time = None
timer = None
CHECKS_PER_SECOND = 100  # Frequency that a check for a long click is made.

root = tk.Tk()
root.geometry('100x100')

def on_button_down(event):
    global start_time, timer

    label.config(text='Click detected')
    start_time = cur_time()
    timing = True
    timer = check_time()


def check_time():
    global timer

    if (cur_time() - start_time) < LONG_CLICK:
        delay = 1000 // CHECKS_PER_SECOND  # Determine millisecond delay.
        timer = root.after(delay, check_time)  # Check again after delay.
    else:
        root.event_generate('<<LongClick-1>>')
        root.after_cancel(timer)
        timer = None


def on_button_up(event):
    global timer

    if timer:
        root.after_cancel(timer)
        timer = None
        label.config(text='Waiting')


def on_long_click(event):
    label.config(text='Long click detected')


label = tk.Label(root, text='Waiting')
label.pack(fill=BOTH, expand=1)

root.bind('<ButtonPress-1>', on_button_down)
root.bind('<ButtonRelease-1>', on_button_up)
root.bind('<<LongClick-1>>', on_long_click)

root.mainloop()