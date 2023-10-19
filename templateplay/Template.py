import cv2
from .TemplateImage import TemplateImage
import numpy as np


class Template:
    base_color = 0  # 0 - 180

    def __init__(self, name):
        self.name = name
        self.images: list[TemplateImage] = []
        self.base_hsv = np.array([[[Template.base_color, 255, 255]]], dtype=np.uint8)
        rect_color = cv2.cvtColor(self.base_hsv, cv2.COLOR_HSV2BGR)
        self.rect_color = (
            int(rect_color[0][0][0]),
            int(rect_color[0][0][1]),
            int(rect_color[0][0][2]),
        )
        Template.base_color += 51
        Template.base_color %= 180

    def add_image(self, path):
        self.images.append(TemplateImage(path))

    def __repr__(self):
        value = "Template: " + self.name + " "
        for img in self.images:
            value += self.images.__repr__()

        return value
