import os
import cv2
import pyautogui
import numpy as np
from typing import Dict, List
from cv2.typing import MatLike, Scalar
from .TemplateImage import TemplateImage
from .Template import Template
from .TemplatePosition import TemplatePosition


if os.name == "nt":
    from .screen_utils_win import Win
else:
    from .screen_utils_linux import WindowCaptureLinux as WindowCapture


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


def find_templates(
    screen: MatLike,
    template_images: dict[str, Template],
    group_threshold=1,
    epsilon=0.2,
):
    positions: List[TemplatePosition] = []
    for name, template in template_images.items():
        for templ_img in template.images:
            result = cv2.matchTemplate(screen, templ_img.img_cv2, cv2.TM_CCOEFF_NORMED)
            yloc, xloc = np.where(result >= np.array(templ_img.threshold))
            if len(xloc):
                # filter duplicates
                rectangles = []
                for l, x in enumerate(xloc):
                    rect = [
                        int(x),
                        int(yloc[l]),
                        int(templ_img.width),
                        int(templ_img.height),
                    ]
                    rectangles.append(rect)
                    # force a duplication so cv2.groupRectangles don't remove
                    # locations that have only one rectangle
                    rectangles.append(rect)
                rectangles, weights = cv2.groupRectangles(
                    rectangles, group_threshold, epsilon
                )
                for rect in rectangles:
                    positions.append(
                        TemplatePosition(
                            templ_img, rect[0], rect[1], template.rect_color
                        )
                    )
    return positions


def draw_rectangles(screen, template_positions: List[TemplatePosition]):
    global running
    for position in template_positions:
        cv2.rectangle(
            screen,
            position.start_position,
            position.end_position,
            position.color,
            position.thickness,
        )

    cv2.imshow("Templates", screen)
    if cv2.waitKey(1) == ord("q"):
        cv2.destroyAllWindows()
        running = False
