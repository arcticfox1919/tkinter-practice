import tkinter as tk
from tkinter import ttk


class Progressbar:
    def start(self, parent=None):
        top = tk.Toplevel()
        self.master = top
        if parent:
            top.transient(parent)

        top.title("网络请求中")
        tk.Label(top, text="请稍等……", fg="green").pack(pady=2)
        prog = ttk.Progressbar(top, mode='indeterminate', length=200)
        prog.pack(pady=10, padx=35)
        prog.start()

        top.resizable(False, False)

        cur_width = top.winfo_width()
        cur_height = top.winfo_height()
        scn_width, scn_height = top.maxsize()
        tmp = '+%d+%d' % ((scn_width - cur_width) / 2, (scn_height - cur_height) / 2)
        top.geometry(tmp)
        top.mainloop()

    def quit(self):
        if self.master:
            self.master.destroy()
