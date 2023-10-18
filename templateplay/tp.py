import os
import cv2
import pyautogui
import numpy as np
from typing import Dict, List


class TemplateImage:
    def __init__(self, path, threshold=0.6):
        self.img_path = path
        self.img_cv2 = cv2.imread(path, cv2.COLOR_RGB2BGR)
        self.threshold = threshold

    def __repr__(self):
        value = self.img_path
        value += " " + str(self.img_cv2.shape)
        return value

    @property
    def width(self):
        return self.img_cv2.shape[0]

    @property
    def height(self):
        return self.img_cv2.shape[1]


class Template:
    base_color = 0  # 0 - 360

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
        Template.base_color %= 360

    def add_image(self, path):
        self.images.append(TemplateImage(path))

    def __repr__(self):
        value = "Template: " + self.name + " "
        for img in self.images:
            value += self.images.__repr__()

        return value


def load_templates(directory: str):
    templates: Dict[str, Template] = dict()
    for root, dir, files in os.walk(directory):
        if len(files):
            template_name = os.path.basename(root)
            if template_name not in templates:
                templates[template_name] = Template(template_name)
            for file in files:
                templates[template_name].add_image(os.path.join(root, file))
    return templates


def screenshot(region):
    # pyautogui.screenshot returns a Pillow Image, which is RGB,
    # but opencv works with BGR
    img = pyautogui.screenshot(region=region)
    np_img = np.array(img)
    cv_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
    return cv_img


class TemplatePosition:
    def __init__(self, template_img: TemplateImage, x: int, y: int):
        self.template_img = template_img
        self.x = x
        self.y = y


def find_templates(screen, template_images: dict[str, Template], group_threshold = 1, epsilon = 0.2):
    positions: List[TemplatePosition] = []
    for name, template in template_images.items():
        for templ_img in template.images:
            result = cv2.matchTemplate(screen, templ_img.img_cv2, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= np.array(templ_img.threshold))
            if len(locations):
                # filter duplicates
                rectangles = []
                for loc in locations:
                    rectangles.append([int(loc[0]), int(loc[1]), int(templ_img.img_cv2.shape[0]), int(templ_img.img_cv2.shape[1])])
                    # force a duplication so cv2.groupRectangles don't remove
                    # locations that have only one rectangle
                    rectangles.append([int(loc[0]), int(loc[1]), int(templ_img.img_cv2.shape[0]), int(templ_img.img_cv2.shape[1])])
                rectangles, weights = cv2.groupRectangles(rectangles, group_threshold, epsilon)
                for rect in rectangles:
                    positions.append(TemplatePosition(templ_img, rect[0], rect[1]))
    return positions


def show(screen, template_positions):
    
