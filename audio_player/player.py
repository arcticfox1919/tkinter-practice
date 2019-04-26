import os, platform, resource

os.environ['PYTHON_VLC_MODULE_PATH'] = resource.PYTHON_VLC_MODULE_PATH

import vlc


class Player:
    play_mode = [vlc.PlaybackMode.default, vlc.PlaybackMode.repeat, vlc.PlaybackMode.loop]

    def __init__(self):
        instance = vlc.Instance("--audio-visual=visual",
                                "--effect-list=spectrum",
                                "--effect-fft-window=flattop")

        # 创建列表播放器
        self.list_player = instance.media_list_player_new()
        # 创建媒体列表
        self.media_list = instance.media_list_new()
        # 给列表播放器设置媒体列表
        self.list_player.set_media_list(self.media_list)
        # 获取当前用于播放的Player
        self.the_player = self.list_player.get_media_player()

    # 向列表中添加流媒体URL或本地文件路径
    def add_uri(self, uri):
        self.media_list.add_media(uri)

    def remove(self, index):
        return self.media_list.remove_index(index)

    def clear(self):
        self.media_list.lock()
        for i in range(self.media_list.count()):
            self.remove(i)
        self.media_list.unlock()

    def item_index(self):
        return self.media_list.index_of_item(self.the_player.get_media())

    # 播放指定索引的媒体
    def play_at(self, index):
        return self.list_player.play_item_at_index(index)

    # 下一曲
    def next(self):
        return self.list_player.next()

    # 上一曲
    def previous(self):
        return self.list_player.previous()

    # 恢复
    def resume(self):
        self.the_player.set_pause(0)

    # 暂停
    def pause(self):
        self.the_player.pause()

    # 停止
    def stop(self):
        self.list_player.stop()

    def release(self):
        return self.list_player.release()

    def is_playing(self):
        return self.the_player.is_playing()

    # 已耗时，返回毫秒值
    def get_time(self):
        return self.the_player.get_time()

    def set_time(self, val):
        return self.the_player.set_time(val)

    # 总长度，返回毫秒值
    def get_length(self):
        return self.the_player.get_length()

    def get_state(self):
        state = self.the_player.get_state()
        if state == vlc.State.Playing:
            return 1
        elif state == vlc.State.Paused:
            return 0
        else:
            return -1

    # 当前播放进度(0.0~1.0之间)
    def get_position(self):
        return self.the_player.get_position()

    # 设置当前播放进度(0.0~1.0之间)
    def set_position(self, float_val):
        self.the_player.set_position(float_val)

    # 获取当前音量（0~100）
    def get_volume(self):
        return self.the_player.audio_get_volume()

    # 设置音量（0~100）
    def set_volume(self, volume):
        return self.the_player.audio_set_volume(volume)

    def mute(self):
        self.the_player.audio_set_mute(True)

    def unmute(self):
        self.the_player.audio_set_mute(False)

    def get_mute(self):
        return self.the_player.audio_get_mute()

    # 0: default
    # 1: loop
    # 2: repeat
    def set_list_mode(self, mode):
        self.list_player.set_playback_mode(self.play_mode[mode])

    # 设置监听，播放已耗时变化时回调
    def add_callback(self, callback):
        self.the_player.event_manager().event_attach(vlc.EventType.MediaPlayerTimeChanged, callback)
        self.the_player.event_manager().event_attach(vlc.EventType.MediaPlayerPlaying, callback)

    # 设置窗口句柄
    def set_window(self, wm_id):
        if platform.system() == 'Windows':
            self.the_player.set_hwnd(wm_id)
        else:
            self.the_player.set_xwindow(wm_id)
