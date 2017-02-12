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


class ScreenClipper(object):
    """ スクリーンショットを撮るための補助GUI """
    # tkinterが使う座標は全てスケールされたものであることに注意

    def __init__(self):
        # self.boxにはスケールされていない座標を使う
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
        img = self.screenshot().crop([dx,
                                      dy,
                                      dx + self.root.winfo_width() * SCREEN_SCALING_FACTOR,
                                      dy + self.root.winfo_height() * SCREEN_SCALING_FACTOR])
        img.save("screenshot_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".jpg")

    @staticmethod
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

if __name__ == "__main__":
    ScreenClipper()
