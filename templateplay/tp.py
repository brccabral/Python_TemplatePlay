import os
import cv2
from typing import Dict


class TemplateImage:
    def __init__(self, path):
        self.img_path = path
        self.img_cv2 = cv2.imread(path, cv2.IMREAD_UNCHANGED)

    def __repr__(self):
        value = self.img_path
        value += " " + str(self.img_cv2.shape)
        return value


class Template:
    def __init__(self, name):
        self.name = name
        self.images: list[TemplateImage] = []

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
    print(f"{region=}")
    return region


def find_templates(screen, template_images):
    print(f"{screen=}")
    print(f"{template_images=}")
    return template_images


def show(screen, template_positions):
    print(f"{screen=}")
    print(f"{template_positions=}")
