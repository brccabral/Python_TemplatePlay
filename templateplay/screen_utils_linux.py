import pyscreenshot as ImageGrab
import numpy as np
import cv2
from .screen_utils import WindowCaptureABC


class WindowCaptureLinux(WindowCaptureABC):
    def screenshot(self, region):
        # using backend="mss", childprocess=False speeds up the grab()
        # https://github.com/ponty/pyscreenshot
        img = ImageGrab.grab(bbox=region, backend="mss", childprocess=False)
        # ImageGrab returns a Pillow Image, which is RGB,
        # but opencv works with BGR
        np_img = np.array(img)
        cv_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
        return cv_img
