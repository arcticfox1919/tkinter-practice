import tkinter as tk
import resource


class AudioVisual(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, height=150, bg="black")
        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.canvas.place(relwidth=1, y=-185)

    def id(self):
        return self.canvas.winfo_id()

    def set_image(self, img):
        self.canvas.create_image(resource.app_width / 2, self.canvas.winfo_reqheight(), image=img, anchor=tk.S)

    def clear(self):
        self.canvas.delete("all")
