# pip install pywin32
from typing import Optional, Tuple
import win32gui
import win32ui
import win32con
import numpy as np
from .screen_utils import WindowCaptureABC


# https://www.youtube.com/watch?v=WymCpVUPWQ4
class WindowCaptureWin(WindowCaptureABC):
    def __init__(
        self,
        *,
        window_name: Optional[str] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
    ):
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            self.hwnd = win32gui.FindWindow(None, window_name)
            if not self.hwnd:
                raise Exception(f"Window not found: {window_name}")

        window_rect = win32gui.GetWindowRect(self.hwnd)
        if region is None:
            region = window_rect

        self.w = region[2] - region[0]
        self.h = region[3] - region[1]

        # because we cropped the image, the actual position on screen needs an offset
        self.offset_x = region[0]
        self.offset_y = region[1]
        self.cropped_x = self.offset_x
        self.cropped_y = self.offset_y

    def screenshot(self):
        # w = region[2] - region[0]
        # h = region[3] - region[1]

        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt(
            (0, 0),
            (self.w, self.h),
            dcObj,
            (self.cropped_x, self.cropped_y),
            win32con.SRCCOPY,
        )

        signedIntsArray = dataBitMap.GetBitmapBits(True)

        # Free resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # convert to screen format
        img = np.fromstring(signedIntsArray, dtype=np.uint8)
        img.shape = (self.h, self.w, 4)
        # drop alpha channel for cv.matchTemplate
        img = img[..., :3]
        # make image contiguous for cv.draw_rectangles
        # https://github.com/opencv/opencv/issues/14866
        img = np.ascontiguousarray(img)

        return img

    @staticmethod
    def list_window_names():
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))

        win32gui.EnumWindows(winEnumHandler, None)

    # is you move the original window, this will be wrong
    def get_screen_position(self, pos):
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)
