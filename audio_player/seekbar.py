import tkinter as tk
from PIL import Image, ImageTk


class Seekbar(tk.Canvas):
    progress_height = 5
    progress_y = 0

    def __init__(self, parent, **options):
        tk.Canvas.__init__(self, parent, options)
        self.parent = parent
        self.width = options['width']
        self.progress_y = (options['height'] - self.progress_height) / 2

        self.create_rectangle(0, self.progress_y, options['width'],
                              self.progress_height + self.progress_y, fill="#333333", width=0)
        self.red_rectangle = self.create_rectangle(0, 0, 0, 0, fill="#939797", width=0)

        image = Image.open("img/seekbar_block.png")

        self.seekbar_knob_image = ImageTk.PhotoImage(image)
        self.seekbar_knob = self.create_image(0, 5, image=self.seekbar_knob_image)
        self.bind_mouse_button()

    def bind_mouse_button(self):
        self.bind('<Button-1>', self.on_seekbar_clicked)
        self.bind('<B1-Motion>', self.on_seekbar_clicked)
        self.tag_bind(
            self.red_rectangle, '<B1-Motion>', self.on_seekbar_clicked)
        self.tag_bind(
            self.seekbar_knob, '<B1-Motion>', self.on_seekbar_clicked)

    def on_seekbar_clicked(self, event):
        if event.x > 0 and event.x < self.width:
            self.move_to_position(event.x)
            self.event_generate("<<SeekbarPositionChanged>>", x=event.x)

    def move_to_position(self, new_position):
        new_position = round(new_position, 1)
        self.coords(self.red_rectangle, 0, self.progress_y, new_position, self.progress_height + self.progress_y)
        self.coords(self.seekbar_knob, new_position, 5)
