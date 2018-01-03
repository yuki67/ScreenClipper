import platform
import tkinter as tk
import time
from datetime import datetime
from PIL import Image
from MyGUI import MyTkBase

if platform.system() == "Windows":
    print("if saved image looks odd, "
          "take a look at SCREEN_SCALING_FACTOR in ScreenClipper.py")
    import win32gui
    import win32ui
    import win32con
    from win32api import GetSystemMetrics
    # グローバル変数
    # どうしても無くせなかった
    SCREEN_SCALING_FACTOR = 1.5

    def screenshot():
        """ スクリーンショット撮ってそれを(Pillow.Imageで)返す """
        window = win32gui.GetDesktopWindow()
        window_dc = win32ui.CreateDCFromHandle(win32gui.GetWindowDC(window))
        compatible_dc = window_dc.CreateCompatibleDC()
        real_width = int(GetSystemMetrics(0) * SCREEN_SCALING_FACTOR)
        real_height = int(GetSystemMetrics(1) * SCREEN_SCALING_FACTOR)
        print(real_width, real_height)
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(window_dc, real_width, real_height)
        compatible_dc.SelectObject(bmp)
        compatible_dc.BitBlt((0, 0), (real_width, real_height), window_dc,
                             (0, 0), win32con.SRCCOPY)
        img = Image.frombuffer('RGB', (real_width, real_height),
                               bmp.GetBitmapBits(True), 'raw', 'BGRX', 0, 1)
        return img
elif platform.system() == "Linux":
    import pyscreenshot as ImageGrab
    SCREEN_SCALING_FACTOR = 1.0
    screenshot = ImageGrab.grab
else:
    print("error: unkonwn platform.")
    exit(0)


class ClipperButton(tk.Button):
    """ 押すとスクリーンショットが保存されるボタン """

    def __init__(self, master):
        super().__init__(master)
        self["text"] = "screenshot"
        self["font"] = ("NanumBarunGothic", 20, "bold")
        self.bind("<Button-1>", self.on_button_click)

    def on_button_click(self, _):
        """ ウィンドウを透明にして画像を保存して透明度を元に戻す """
        self.master.attributes("-alpha", 0.0)
        # アルファチャンネルの変更をフラッシュ
        self.master.bell()
        print("saving image...")
        # ウィンドウを透明にする処理に時間がかかることがあるので適当に待つ
        # 速度なんて誰も気にしない
        time.sleep(1.0)
        self.clip_and_save()
        # 処理が終わってからウィンドウを戻す
        self.master.attributes("-alpha", 0.5)

    def clip_and_save(self):
        """ self.boxのスクリーンショットを取って保存する """
        dx = self.master.winfo_rootx() * SCREEN_SCALING_FACTOR
        dy = self.master.winfo_rooty() * SCREEN_SCALING_FACTOR
        img = screenshot().crop([
            int(dx),  # 整数でないとエラーが出る
            int(dy),
            int(dx + self.master.winfo_width() * SCREEN_SCALING_FACTOR),
            int(dy + self.master.winfo_height() * SCREEN_SCALING_FACTOR)
        ])
        img.save("screenshot_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") +
                 ".jpg")


class TextBox(tk.Label):
    """ 現在のウィンドウの大きさを表示するラベル """

    def __init__(self, master):
        super().__init__(master, justify=tk.CENTER)
        self["text"] = "size: %dx%d" % (
            master.winfo_width() * SCREEN_SCALING_FACTOR,
            master.winfo_height() * SCREEN_SCALING_FACTOR)
        self["font"] = ("NanumBarunGothic", 20, "bold")
        self.bind('<Configure>', self.on_size_changed)

    def on_size_changed(self, _):
        """ テキストを変更 """
        self["text"] = "size: %dx%d" % (
            self.master.winfo_width() * SCREEN_SCALING_FACTOR,
            self.master.winfo_height() * SCREEN_SCALING_FACTOR)


class ResizeButton(tk.Button):
    """ 押されるとリサイズを実行するボタン """

    def __init__(self, master, entry):
        super().__init__(master)
        self["text"] = "resize"
        self["font"] = ("NanumBarunGothic", 20, "bold")
        self.entry = entry
        self.bind("<Button-1>", self.on_button_click)

    def on_button_click(self, _):
        """ エントリからサイズを読み取ってリサイズする """
        string = self.entry.get()
        try:
            w, h = string.split("x")
            w, h = int(w) / SCREEN_SCALING_FACTOR, int(
                h) / SCREEN_SCALING_FACTOR
        except ValueError:
            return
        self.master.geometry("%dx%d" % (int(w), int(h)))


class ResizeEntry(tk.Entry):
    """ リサイズするときにサイズを入力する場所 """

    def __init__(self, master):
        super().__init__(master, justify=tk.CENTER)
        self["font"] = ("NanumBarunGothic", 20, "bold")
        self.insert(tk.END,
                    "%dx%d" % (master.winfo_width() * SCREEN_SCALING_FACTOR,
                               master.winfo_height() * SCREEN_SCALING_FACTOR))
        self.bind('<Configure>', self.on_size_changed)

    def on_size_changed(self, _):
        """ テキストを変更 """
        self.delete(0, tk.END)
        self.insert(tk.END, "%dx%d" %
                    (self.master.winfo_width() * SCREEN_SCALING_FACTOR,
                     self.master.winfo_height() * SCREEN_SCALING_FACTOR))


class MyTk(MyTkBase):
    def __init__(self, width, height, name):
        super().__init__(width, height, name)
        self.attributes("-alpha", 0.5)
        ClipperButton(self).pack(fill=tk.X)
        TextBox(self).pack(fill=tk.X)
        entry = ResizeEntry(self)
        entry.pack(fill=tk.X)
        ResizeButton(self, entry).pack(fill=tk.X)
        self.mainloop()


if __name__ == "__main__":
    root = MyTk(500, 500, "Screen Clipper")
