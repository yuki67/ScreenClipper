""" tkinterのクラスを自分が使いやすい様に改造したもの """
import tkinter


class MyCanvasBase(tkinter.Canvas):
    """ Canvasに自作関数を追加したもの """

    def __init__(self, master):
        super().__init__(master, width=master.winfo_width(), height=master.winfo_height())
        self.place(x=0, y=0)

    def create_grid(self, space):
        """ 幅spaceでグリッドを描く """
        w, h = self.master.winfo_width(), self.master.winfo_height()
        for x in range(0, w, space):
            self.create_line([x, 0, x, h], fill="yellow")
        for y in range(0, h, space):
            self.create_line([0, y, w, y], fill="yellow")

    def create_loop(self, points):
        """ pointsをその順番に一周するループを描く """
        if len(points) > 1:
            self.create_line(points, tag="loop")
            self.create_line([points[-1], points[0]], tag="loop")

    def create_circle(self, center, r, text=""):
        """ 中心center, 半径rの円を描く """
        self.create_oval([center[0] - r, center[1] - r, center[0] + r, center[1] + r], fill="red")
        self.create_text(center[0], center[1], text=text, font=('FixedSys', 14), fill="yellow")


class MyTkBase(tkinter.Tk):
    """ Tkを使いやすくまとめたもの """

    def __init__(self, width, height, name="My window"):
        super().__init__()
        self.wm_title(name)
        self.geometry("%dx%d" % (width, height))
        self.update()
