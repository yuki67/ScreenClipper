import tkinter
from datetime import datetime
import win32gui
import win32ui
import win32con
from PIL import Image

# グローバル変数
# どうしても無くせなかった
SCREEN_WIDTH = 2160
SCREEN_HEIGHT = 1440
SCREEN_SCALING_FACTOR = 1.5


class ScreenCamera(object):
    """ スクリーンショットを取る(だけ) """
    # PIL.ImageGrab.grab()がWindowsだとうまくいかないので自分で書き直した

    # pylintでwin32guiの関数が見つからないというエラーが出るが、ちゃんと動く
    def __init__(self):
        self.window_dc = win32ui.CreateDCFromHandle(win32gui.GetWindowDC(win32gui.GetDesktopWindow()))
        self.compatible_dc = self.window_dc.CreateCompatibleDC()
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT

    def screenshot(self):
        """ スクリーンショット撮ってそれを(Pillow.Imageで)返す """
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(self.window_dc, self.width, self.height)
        self.compatible_dc.SelectObject(bmp)
        self.compatible_dc.BitBlt((0, 0), (self.width, self.height), self.window_dc, (0, 0), win32con.SRCCOPY)
        img = Image.frombuffer('RGB', (self.width, self.height), bmp.GetBitmapBits(True), 'raw', 'BGRX', 0, 1)
        return img


class ScreenClipper(object):
    """ スクリーンショットを撮るための補助GUI """
    # tkinterが使う座標は全てスケールされたものであることに注意

    def __init__(self):
        # self.boxにはスケールされていない座標を使う
        self.camera = ScreenCamera()
        self.root = tkinter.Tk()
        self.root.title("ScreenClipper")
        self.root.attributes("-alpha", 0.5)
        self.root.geometry("%dx%d+%d+%d" % (500, 500, 0, 0))
        self.place_button()
        self.root.mainloop()

    def place_button(self):
        """ ボタンを配置する """
        button = tkinter.Button(text='screenshot', bg="blue", fg="yellow")
        button.bind("<Button-1>", self.on_button_click)
        button.pack()

    def on_button_click(self, event):
        """ コールバック関数 """
        self.root.attributes("-alpha", 0.0)
        self.clip_and_save()
        self.root.attributes("-alpha", 0.5)

    def clip_and_save(self):
        """ self.boxのスクリーンショットを取って保存する """
        dx = self.root.winfo_rootx() * 1.5
        dy = self.root.winfo_rooty() * 1.5 + 1
        img = self.camera.screenshot().crop([dx,
                                             dy,
                                             dx + self.root.winfo_width() * SCREEN_SCALING_FACTOR,
                                             dy + self.root.winfo_height() * SCREEN_SCALING_FACTOR])
        img.save("screenshot_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".jpg")


if __name__ == "__main__":
    ScreenClipper()
