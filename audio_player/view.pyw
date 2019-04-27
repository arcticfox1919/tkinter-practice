from tkinter import *
import tkinter.ttk as ttk
from tkinter.font import Font
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from resource import *
from seekbar import Seekbar
from player import Player
from audio_visual import AudioVisual
from progressbar import Progressbar
import Pmw, os, sys, utils, vlc


class AudioView(Tk):
    loop_choices = [("不循环", 0), ("单曲循环", 1), ("列表循环", 2)]
    icon_res = []
    current_selected = 0

    def __init__(self):
        super().__init__()
        self._init_data_()
        self._set_window_()
        self._create_menu_bar()
        self._create_top_view()
        self._create_control_panel()
        self._create_list_box()
        self._create_context_menu()
        self._create_bottom_view()

    def _init_data_(self):
        for icon in control_icon:
            self.icon_res.append(PhotoImage(file='img/%s.gif' % icon))

        for icon in bottom_icon:
            self.icon_res.append(PhotoImage(file='img/%s.gif' % icon))

        self.player = Player()
        self.player.add_callback(self._media_playing)
        self.bind("<<SeekbarPositionChanged>>", self.seek_new_position)

        self.request = utils.RequestTask()
        self.progressbar = Progressbar()

    # 设置初始窗口的属性
    def _set_window_(self):
        self["bg"] = "black"
        self.title("AudioPlayer")
        self.wm_attributes("-alpha", window_alpha)
        scn_width, scn_height = self.maxsize()
        wm_val = '%dx%d+%d+%d' % (app_width, app_height,
                                  (scn_width - app_width) / 2, (scn_height - app_height) / 2)
        self.geometry(wm_val)
        self.resizable(False, False)
        self.iconbitmap("img/player.ico")
        self.protocol('WM_DELETE_WINDOW', self.exit_player)

    # 创建菜单栏
    def _create_menu_bar(self):
        menu_bar = Menu(self)
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label='打开文件', accelerator='Ctrl+O',
                              command=lambda: self.show_dialog("file"))
        file_menu.add_command(label='打开目录', accelerator='Ctrl+Shift+O',
                              command=lambda: self.show_dialog("dir"))

        file_menu.add_separator()
        file_menu.add_command(label='退出', accelerator='Alt+F4', command=self.exit_player)

        menu_bar.add_cascade(label='文件', menu=file_menu)

        about_menu = Menu(menu_bar, tearoff=0)
        about_menu.add_command(label='关于', command=lambda: self.show_messagebox(0))
        about_menu.add_command(label='帮助', command=lambda: self.show_messagebox(1))
        menu_bar.add_cascade(label='关于', menu=about_menu)
        self["menu"] = menu_bar

    @staticmethod
    def show_messagebox(what):
        if what == 0:
            messagebox.showinfo("关于", abort_content)
        else:
            messagebox.showinfo("帮助", help_content, icon='question')

    # 创建音频信息面板
    def _create_top_view(self):
        image = Image.open(default_avatar)
        image = image.resize((avatar_width, avatar_height))
        self.photo = ImageTk.PhotoImage(image)

        self.audio_visual = AudioVisual(self)
        self.audio_visual.set_image(self.photo)
        self.audio_visual.pack(fill=BOTH)
        self.player.set_window(self.audio_visual.id())

        f = Font(family='微软雅黑', size=-20)
        self.audio_name = Message(self, text="未知", fg="white", bg="black", font=f, aspect=600)
        self.audio_name.pack()
        self.audio_time = Label(self, text="00:00/00:00", fg="white", bg="black")
        self.audio_time.pack()
        self.seek_bar = Seekbar(self, background="black", width=SEEKBAR_WIDTH, height=10, highlightthickness=0)
        self.seek_bar.pack(pady=15, padx=15, fill="x")

    # 创建控制面板
    def _create_control_panel(self):
        self.balloon = Pmw.Balloon(self)
        frame = Frame(self)
        previous_btn = Button(frame, image=self.icon_res[0], borderwidth=0, padx=0,
                              command=lambda: self._audio_control("previous"))
        previous_btn.grid(row=3, column=1, sticky='w')
        self.balloon.bind(previous_btn, '上一首')

        rewind_btn = Button(frame, image=self.icon_res[1], borderwidth=0, padx=0,
                            command=lambda: self._audio_control("rewind"))
        rewind_btn.grid(row=3, column=2, sticky='w')
        self.balloon.bind(rewind_btn, '快退')

        self.play_icon, self.pause_icon = self.icon_res[2], self.icon_res[3]
        self.play_pause_btn = Button(frame, image=self.play_icon, borderwidth=0, padx=0,
                                     command=lambda: self._audio_control("play"))
        self.play_pause_btn.grid(row=3, column=3)
        self.balloon.bind(self.play_pause_btn, '播放/暂停')

        stop_btn = Button(frame, image=self.icon_res[4], borderwidth=0, padx=0,
                          command=lambda: self._audio_control("stop"))
        stop_btn.grid(row=3, column=4)
        self.balloon.bind(stop_btn, '停止')

        fast_forward_btn = Button(frame, image=self.icon_res[5], borderwidth=0, padx=0,
                                  command=lambda: self._audio_control("forward"))
        fast_forward_btn.grid(row=3, column=5)
        self.balloon.bind(fast_forward_btn, '快进')

        next_track_btn = Button(frame, image=self.icon_res[6], borderwidth=0, padx=0,
                                command=lambda: self._audio_control("next"))
        next_track_btn.grid(row=3, column=6)
        self.balloon.bind(next_track_btn, '下一首')

        self.mute_icon, self.unmute_icon = self.icon_res[7], self.icon_res[8]
        img = self.mute_icon if self.player.get_mute() else self.unmute_icon
        self.mute_unmute_btn = Button(frame, image=img, borderwidth=0, padx=0,
                                      command=lambda: self._audio_control("unmute"))
        self.mute_unmute_btn.grid(row=3, column=7)
        self.balloon.bind(self.mute_unmute_btn, '静音/恢复')

        self.volume_scale = ttk.Scale(frame, from_=0, to=100, length=130,
                                      command=lambda evt: self._audio_control("volume"))
        self.volume_scale.set(80)
        self.player.set_volume(int(self.volume_scale.get()))
        self.volume_scale.grid(row=3, column=8, padx=5)
        frame.pack(fill="x", padx=30)

    def _create_list_box(self):
        menu_frame = Frame(bg="black")
        Label(menu_frame, text="播放列表", bg="black", fg="white",
              font=("微软雅黑", -22)).pack(side="left")
        self.outline_btn = Button(menu_frame, text="在线音乐", bg="white", activeforeground="#E98D44",
                                  fg="#EA2000", padx=0, pady=0, bd=0, command=self.request_outline_music)
        self.outline_btn.pack(side="left", padx=6)

        # 播放列表框
        frame = LabelFrame(self, labelwidget=menu_frame, bg="black", borderwidth=2,
                           padx=10, pady=8, relief="sunken")

        y_bar = Scrollbar(frame, orient=VERTICAL, bd=0, width=14)
        x_bar = Scrollbar(frame, orient=HORIZONTAL, bd=0, width=14)

        # 创建列表框
        self.list_box = Listbox(frame, bg="black", yscrollcommand=y_bar.set, fg="white",
                                xscrollcommand=x_bar.set, border=0, highlightthickness=0,
                                selectforeground="#F0F126", selectbackground="black",
                                activestyle="none", font=("微软雅黑", -18), height=8)

        self.list_box.bind('<Double-Button-1>', self.list_selected)
        self.list_box.bind("<Button-3>", self.show_context_menu)

        y_bar['command'] = self.list_box.yview
        x_bar['command'] = self.list_box.xview

        y_bar.pack(side=RIGHT, fill=Y)
        x_bar.pack(side=BOTTOM, fill=X)
        self.list_box.pack(anchor=NW, fill=BOTH, expand=YES)
        frame.pack(fill="both", padx=10, pady=15, expand="yes")

    # 创建底部功能栏
    def _create_bottom_view(self):
        frame = Frame(self)
        add_btn = Button(frame, image=self.icon_res[9], borderwidth=0, padx=0,
                         command=lambda: self.show_dialog("file"))
        add_btn.grid()
        self.balloon.bind(add_btn, '添加文件')

        remove_selected_btn = Button(frame, image=self.icon_res[10], borderwidth=0, padx=0,
                                     command=lambda: self.remove_at(self.current_selected))
        remove_selected_btn.grid(row=0, column=1)
        self.balloon.bind(remove_selected_btn, '删除选中')

        add_dir_btn = Button(frame, image=self.icon_res[11], borderwidth=0, padx=0,
                             command=lambda: self.show_dialog("dir"))
        add_dir_btn.grid(row=0, column=2)
        self.balloon.bind(add_dir_btn, '添加目录')

        clear_list_btn = Button(frame, image=self.icon_res[12], borderwidth=0, padx=0,
                                command=self.clear_list)
        clear_list_btn.grid(row=0, column=3)
        self.balloon.bind(clear_list_btn, '清空播放列表')

        self.loop_value = IntVar()
        self.loop_value.set(2)
        for txt, val in self.loop_choices:
            Radiobutton(frame, text=txt, variable=self.loop_value, value=val,
                        command=self.on_mode_select).grid(row=0, column=4 + val, pady=3, padx=2)

        self.player.set_list_mode(self.loop_value.get())
        frame.pack(fill="x")

    def _create_context_menu(self):
        self.context_menu = Menu(self.list_box, tearoff=0)
        self.context_menu.add_command(label="删除")

    def show_context_menu(self, event):
        # 清除鼠标右键选中色
        for i in range(self.list_box.size()):
            self.list_box.itemconfig(i, background="black")

        # 获取当前鼠标右键选中的索引
        index = self.list_box.nearest(event.y)
        # 选中后改变背景色
        self.list_box.itemconfig(index, background="gray")

        self.context_menu.entryconfigure(0, command=lambda: self.remove_at(index))
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def show_dialog(self, what):
        if what == "file":
            input_file = filedialog.askopenfilename(
                filetypes=[("所有文件", "*.*"), ("MP3", "*.mp3")])
            if input_file:
                self._add_audio_file(input_file)
        elif what == "dir":
            dir_name = filedialog.askdirectory()
            if dir_name:
                for file_name in os.listdir(dir_name):
                    file_path = os.path.join(dir_name, file_name)
                    if os.path.isfile(file_path):
                        self._add_audio_file(file_path)

    def _add_audio_file(self, file_path):
        file_name = os.path.basename(file_path)
        # 加入ListBox
        self.list_box.insert("end", file_name)
        # 加入到媒体列表
        self.player.add_uri(file_path)
        if self.list_box.size() == 1:
            self.list_box.selection_set(self.current_selected)

    def list_selected(self, event):
        self.current_selected = self.list_box.curselection()[0]
        self.list_box.selection_set(self.current_selected)
        self.play_pause_btn.config(image=self.pause_icon)
        self._play_audio()

    def _audio_control(self, op):
        if not hasattr(self, "list_box") or self.list_box.size() == 0:
            return

        if op == "play":
            self.list_box.select_clear(0, "end")
            self.list_box.select_set(self.current_selected)
            state = self.player.get_state()
            if state == 1:  # 正在播放，则暂停
                self.player.pause()
                self.play_pause_btn.config(image=self.play_icon)
            elif state == 0:  # 已暂停，则继续
                self.player.resume()
                self.play_pause_btn.config(image=self.pause_icon)
            else:
                self.list_box.see(self.current_selected)
                self._play_audio()
                self.play_pause_btn.config(image=self.pause_icon)
        elif op == "stop":
            self.player.stop()
            self.play_pause_btn.config(image=self.play_icon)
            self.audio_name.config(text="未知")
            self._update_audio_time(False)
        elif op == "next":
            if self.current_selected < self.list_box.size():
                self.list_box.select_clear(0, "end")
                self.current_selected += 1
                self.list_box.selection_set(self.current_selected)
                self.list_box.see(self.current_selected)
                self.player.next()
        elif op == "previous":
            if self.current_selected > 0:
                self.list_box.select_clear(0, "end")
                self.current_selected -= 1
                self.list_box.selection_set(self.current_selected)
                self.list_box.see(self.current_selected)
                self.player.previous()
        elif op == "unmute":
            if self.player.get_mute():
                self.mute_unmute_btn.config(image=self.unmute_icon)
                self.player.unmute()
            else:
                self.mute_unmute_btn.config(image=self.mute_icon)
                self.player.mute()
        elif op == "volume":
            self.player.set_volume(int(self.volume_scale.get()))

        elif op == "rewind":  # 默认快退10秒
            val = self.player.get_time()
            if val - 10000 < 0:
                val = 0
            else:
                val -= 10000
            self.player.set_time(val)
        elif op == "forward":  # 默认快进10秒
            val = self.player.get_time()
            if val + 10000 > self.player.get_length():
                val = self.player.get_length() - 100
            else:
                val += 10000
            self.player.set_time(val)

    def _play_audio(self):
        self.player.play_at(self.current_selected)

    def seek_new_position(self, event):
        value = event.x / SEEKBAR_WIDTH
        self.player.set_position(utils.round_val(value))

    def _media_playing(self, event):
        if event.type == vlc.EventType.MediaPlayerPlaying:
            self.list_box.select_clear(0, "end")
            self.current_selected = self.player.item_index()
            self.list_box.selection_set(self.current_selected)
            self.audio_name.config(text=self.list_box.get(self.current_selected))
        else:
            self.seek_bar.move_to_position(self.player.get_position() * SEEKBAR_WIDTH)
            self._update_audio_time(True)

    def _update_audio_time(self, update):
        if update:
            total = self.player.get_length()
            cur_time = self.player.get_time()
            format_str = "{}/{}".format(utils.compute_time(cur_time), utils.compute_time(total))
            self.audio_time.config(text=format_str)
        else:
            self.audio_time.config(text="00:00/00:00")

    def on_mode_select(self):
        self.player.set_list_mode(self.loop_value.get())

    def clear_list(self):
        self._audio_control("stop")
        self.list_box.delete(0, "end")
        self.player.clear()

    def remove_at(self, index):
        self._audio_control("stop")
        self.list_box.delete(index)
        self.player.remove(index)

    def request_outline_music(self):
        self.outline_btn.config(state="disable")
        self.request.request(utils.BASE_URL, music_limit)
        self._check_task()
        self.progressbar.start(self)

    def _check_task(self):
        if self.request.check_task():
            self.progressbar.quit()
            self.outline_btn.config(state="normal")
            b, r = self.request.get_result()
            if b:
                for music in r:
                    self.list_box.insert("end", "%s - %s" % (music.name, music.singer))
                    # 加入到媒体列表
                    self.player.add_uri(music.url)
                    if self.list_box.size() == 1:
                        self.list_box.selection_set(self.current_selected)
        else:
            self.after(1000, self._check_task)

    def exit_player(self):
        self.quit()
        self.destroy()
        sys.exit()


if "__main__" == __name__:
    app = AudioView()
    app.mainloop()
