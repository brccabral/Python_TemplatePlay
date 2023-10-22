from typing import Optional, Tuple
import numpy as np
import cv2
from .screen_utils import WindowCaptureABC

import screenshot as sc
import ctypes
from PIL import Image


class WindowCaptureLinux(WindowCaptureABC):
    def __init__(
        self,
        *,
        window_name: Optional[str] = None,
        region: Optional[Tuple[int, int, int, int]] = None
    ):
        if window_name:
            raise Exception("Don't use window_name on Linux, use region")
        if region:
            self.region = region
        else:
            self.region = (0, 0, 1920, 1080)

        self.x = self.region[0]
        self.y = self.region[1]
        self.w = self.region[2] - self.region[0]
        self.h = self.region[3] - self.region[1]
        size = self.w * self.h
        objlength = size * 3
        self.result = (ctypes.c_ubyte * objlength)()

    def screenshot(self):
        sc.take(self.x, self.y, self.w, self.h, self.result)
        screenshot = Image.frombuffer("RGB", (self.w, self.h), self.result, "raw", "RGB", 0, 1)
        screenshot = np.array(screenshot)
        # opencv works with BGR
        cv_img = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        return cv_img
