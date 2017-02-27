import tkinter
from datetime import datetime
import win32gui
import win32ui
import win32con
from PIL import Image
from MyGUI import MyTkBase

# グローバル変数
# どうしても無くせなかった
SCREEN_WIDTH = 2160
SCREEN_HEIGHT = 1440
SCREEN_SCALING_FACTOR = 1.5


def screenshot():
    """ スクリーンショット撮ってそれを(Pillow.Imageで)返す """
    window = win32gui.GetDesktopWindow()
    window_dc = win32ui.CreateDCFromHandle(win32gui.GetWindowDC(window))
    compatible_dc = window_dc.CreateCompatibleDC()
    width = SCREEN_WIDTH
    height = SCREEN_HEIGHT
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(window_dc, width, height)
    compatible_dc.SelectObject(bmp)
    compatible_dc.BitBlt((0, 0), (width, height), window_dc, (0, 0), win32con.SRCCOPY)
    img = Image.frombuffer('RGB', (width, height), bmp.GetBitmapBits(True), 'raw', 'BGRX', 0, 1)
    return img


class ClipperButton(tkinter.Button):
    """ 押すとスクリーンショットが保存されるボタン """

    def __init__(self, master):
        super().__init__(master)
        self["text"] = "screenshot"
        self["font"] = ("Arial", 20, "bold")
        self["bg"] = "blue"
        self["fg"] = "yellow"
        self.bind("<Button-1>", self.on_button_click)

    def on_button_click(self, _):
        """ ウィンドウを透明にして画像を保存して透明度を元に戻す """
        self.master.attributes("-alpha", 0.0)
        self.clip_and_save()
        self.master.attributes("-alpha", 0.5)

    def clip_and_save(self):
        """ self.boxのスクリーンショットを取って保存する """
        dx = self.master.winfo_rootx() * 1.5
        dy = self.master.winfo_rooty() * 1.5
        img = screenshot().crop([dx,
                                 dy,
                                 dx + self.master.winfo_width() * SCREEN_SCALING_FACTOR,
                                 dy + self.master.winfo_height() * SCREEN_SCALING_FACTOR])
        img.save("screenshot_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".jpg")


class TextBox(tkinter.Label):
    """ 現在のウィンドウの大きさを表示するラベル """

    def __init__(self, master):
        super().__init__(master)
        self["text"] = "size: %dx%d" % (master.winfo_width() * SCREEN_SCALING_FACTOR, master.winfo_height() * SCREEN_SCALING_FACTOR)
        self["font"] = ("Arial", 20, "bold")
        self.bind('<Configure>', self.on_size_changed)

    def on_size_changed(self, _):
        """ テキストを変更 """
        self["text"] = "size: %dx%d" % (self.master.winfo_width() * SCREEN_SCALING_FACTOR, self.master.winfo_height() * SCREEN_SCALING_FACTOR)


class ResizeButton(tkinter.Button):
    """ 押されるとリサイズを実行するボタン """

    def __init__(self, master, entry):
        super().__init__(master)
        self["text"] = "resize"
        self.entry = entry
        self.bind("<Button-1>", self.on_button_click)

    def on_button_click(self, _):
        """ エントリからサイズを読み取ってリサイズする """
        string = self.entry.get()
        try:
            w, h = string.split("x")
            w, h = int(w) / SCREEN_SCALING_FACTOR, int(h) / SCREEN_SCALING_FACTOR
        except ValueError:
            return
        self.master.geometry("%dx%d" % (int(w), int(h)))


class ResizeEntry(tkinter.Entry):
    """ リサイズするときにサイズを入力する場所 """

    def __init__(self, master):
        super().__init__(master)
        self["font"] = ("Arial", 20, "bold")
        self.insert(tkinter.END, "%dx%d" % (master.winfo_width() * SCREEN_SCALING_FACTOR, master.winfo_height() * SCREEN_SCALING_FACTOR))
        self.bind('<Configure>', self.on_size_changed)

    def on_size_changed(self, _):
        """ テキストを変更 """
        self.delete(0, tkinter.END)
        self.insert(tkinter.END, "%dx%d" % (self.master.winfo_width() * SCREEN_SCALING_FACTOR, self.master.winfo_height() * SCREEN_SCALING_FACTOR))


class MyTk(MyTkBase):

    def __init__(self, width, height, name):
        super().__init__(width, height, name)
        self.attributes("-alpha", 0.5)
        ClipperButton(self).pack()
        TextBox(self).pack()
        entry = ResizeEntry(self)
        entry.pack()
        ResizeButton(self, entry).pack()
        self.mainloop()

if __name__ == "__main__":
    root = MyTk(500, 500, "Screen Clipper")
