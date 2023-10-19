from .TemplateImage import TemplateImage
from cv2.typing import Scalar


class TemplatePosition:
    def __init__(
        self, template_img: TemplateImage, x: int, y: int, color: Scalar, thickness=2
    ):
        self.template_img = template_img
        self.x = x
        self.y = y
        self.color = color
        self.thickness = thickness

    @property
    def start_position(self):
        return (self.x, self.y)

    @property
    def end_position(self):
        return (
            self.x + self.template_img.width,
            self.y + self.template_img.height,
        )

    def __repr__(self):
        value = self.template_img.img_path
        value += " " + str(self.x) + " " + str(self.y)
        value += " " + str(self.color)
        return value
