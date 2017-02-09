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
        self.camera = ScreenCamera()
        self.tk_root = self.setup_tk()
        # self.boxにはスケールされていない座標を使う
        self.box = [SCREEN_WIDTH / 4, SCREEN_HEIGHT / 4, SCREEN_WIDTH / 4 * 3, SCREEN_HEIGHT / 4 * 3]
        self.draw_box()
        self.place_button()
        self.tk_root.mainloop()

    def setup_tk(self):
        """ Tkを組み立てる """
        root = tkinter.Tk()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.title("ScreenCamera")
        root.attributes("-alpha", 0.5)
        root.attributes("-topmost", "true")
        root.geometry("%dx%d+%d+%d" % (width, height, 0, 0))
        return root

    def draw_box(self):
        """ self.boxを描画する """
        # canvasに渡す座標はスケールされたものであることに注意
        canvas = tkinter.Canvas(self.tk_root, width=self.tk_root.winfo_screenwidth(), height=self.tk_root.winfo_screenheight())
        scaled_box = [x / SCREEN_SCALING_FACTOR for x in self.box]
        canvas.create_line((scaled_box[0], scaled_box[1], scaled_box[0], scaled_box[3]))
        canvas.create_line((scaled_box[0], scaled_box[1], scaled_box[2], scaled_box[1]))
        canvas.create_line((scaled_box[2], scaled_box[3], scaled_box[0], scaled_box[3]))
        canvas.create_line((scaled_box[2], scaled_box[3], scaled_box[2], scaled_box[1]))
        canvas.place(x=0, y=0)

    def place_button(self):
        """ ボタンを配置する """
        button = tkinter.Button(text='screenshot')
        button.bind("<Button-1>", self.on_button_click)
        button.pack()

    def on_button_click(self, event):
        """ コールバック関数 """
        self.tk_root.attributes("-alpha", 0.0)
        self.clip_and_save()
        self.tk_root.attributes("-alpha", 0.5)

    def clip_and_save(self):
        """ self.boxのスクリーンショットを取って保存する """
        # ウィンドウのずれを補正
        # root.winfo*()で得られる座標はスケールされたものであることに注意
        dx = self.tk_root.winfo_rootx() * 1.5
        dy = self.tk_root.winfo_rooty() * 1.5 + 1
        img = self.camera.screenshot().crop([self.box[0] + dx, self.box[1] + dy, self.box[2] + dx, self.box[3] + dy])
        img.show()
        # img.save("screenshot_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".jpg")


if __name__ == "__main__":
    ScreenClipper()
