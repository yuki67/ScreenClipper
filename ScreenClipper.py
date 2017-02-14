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

    def __init__(self, master, text, bg, fg):
        super().__init__(master)
        self["text"] = text
        self["bg"] = bg
        self["fg"] = fg
        self.bind("<Button-1>", self.on_button_click)

    def on_button_click(self, event):
        """ コールバック関数 """
        self.master.master.attributes("-alpha", 0.0)
        self.clip_and_save()
        self.master.master.attributes("-alpha", 0.5)

    def clip_and_save(self):
        """ self.boxのスクリーンショットを取って保存する """
        dx = self.master.master.winfo_rootx() * 1.5
        dy = self.master.master.winfo_rooty() * 1.5 + 1
        img = screenshot().crop([dx,
                                 dy,
                                 dx + self.master.master.winfo_width() * SCREEN_SCALING_FACTOR,
                                 dy + self.master.master.winfo_height() * SCREEN_SCALING_FACTOR])
        img.save("screenshot_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".jpg")


class ScreenClipper(tkinter.Frame):

    def __init__(self, master):
        super().__init__(master)
        ClipperButton(self, text='screenshot', bg="blue", fg="yellow").pack()
        self.pack()
        self.master.mainloop()


class MyTk(MyTkBase):

    def __init__(self, width, height, name):
        super().__init__(width, height, name)
        self.attributes("-alpha", 0.5)

if __name__ == "__main__":
    root = MyTk(500, 500, "Screen Clipper")
    ScreenClipper(root)
