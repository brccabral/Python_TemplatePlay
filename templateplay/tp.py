from collections import defaultdict
import os
import cv2
import numpy as np
from typing import Dict, List, Sequence
from cv2.typing import MatLike, Rect
from .Template import Template
from .TemplatePosition import TemplatePosition
from .TemplateImage import TemplateImage
import threading
from concurrent.futures import ThreadPoolExecutor


if os.name == "nt":
    from .screen_utils_win import WindowCapture
else:
    from .screen_utils_linux import WindowCaptureLinux as WindowCapture


class TemplatePlay:
    def __init__(self):
        self.running = True
        self.window = WindowCapture()
        self.TRACKWINDOW = "TRACKWINDOW"

        self.hsv_filter = defaultdict(int)

        self.executor = ThreadPoolExecutor(max_workers=10)

    def load_templates(self, directory: str):
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
        self,
        screen: MatLike,
        template_images: dict[str, Template],
        group_threshold=1,
        epsilon=0.2,
    ):
        templ_positions: List[TemplatePosition] = []

        def get_positions(
            screen, templ_img: TemplateImage, color, group_threshold, epsilon
        ):
            positions = []
            result = cv2.matchTemplate(screen, templ_img.img_cv2, cv2.TM_CCOEFF_NORMED)
            # returns [Y..], [X...]
            locations = np.where(result >= np.array(templ_img.threshold))
            # organize as [(x, y)...]
            locations = list(zip(*locations[::-1]))
            # filter duplicates
            rectangles: Sequence[Rect] = []
            for x, y in locations:
                rect = [
                    int(x),
                    int(y),
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
                    TemplatePosition(templ_img, rect[0], rect[1], color)
                )
            return positions

        returned_msgs = []

        for name, template in template_images.items():
            for templ_img in template.images:
                # rectangles = get_rects(templ_img)
                returned_future_msg = self.executor.submit(
                    get_positions,
                    screen,
                    templ_img,
                    template.rect_color,
                    group_threshold,
                    epsilon,
                )
                returned_msgs.append(returned_future_msg)

        # join threads
        for r in returned_msgs:
            templ_positions += r.result()

        return templ_positions

    def draw_rectangles(self, screen, template_positions: List[TemplatePosition]):
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
            self.running = False

    def init_control_gui(self):
        cv2.namedWindow(self.TRACKWINDOW, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.TRACKWINDOW, 350, 700)

        def callback(value, indicator):
            print(f"{indicator} {value}")
            self.hsv_filter[indicator] = value

        cv2.createTrackbar(
            "HMin", self.TRACKWINDOW, 0, 179, lambda value: callback(value, "HMin")
        )
        cv2.createTrackbar(
            "SMin", self.TRACKWINDOW, 0, 255, lambda value: callback(value, "SMin")
        )
        cv2.createTrackbar(
            "VMin", self.TRACKWINDOW, 0, 255, lambda value: callback(value, "VMin")
        )

        cv2.createTrackbar(
            "HMax", self.TRACKWINDOW, 0, 179, lambda value: callback(value, "HMax")
        )
        cv2.createTrackbar(
            "SMax", self.TRACKWINDOW, 0, 255, lambda value: callback(value, "SMax")
        )
        cv2.createTrackbar(
            "VMax", self.TRACKWINDOW, 0, 255, lambda value: callback(value, "VMax")
        )

        cv2.setTrackbarPos("HMax", self.TRACKWINDOW, 179)
        cv2.setTrackbarPos("SMax", self.TRACKWINDOW, 255)
        cv2.setTrackbarPos("VMax", self.TRACKWINDOW, 255)

        cv2.createTrackbar(
            "SAdd", self.TRACKWINDOW, 0, 255, lambda value: callback(value, "SAdd")
        )
        cv2.createTrackbar(
            "SSub", self.TRACKWINDOW, 0, 255, lambda value: callback(value, "SSub")
        )
        cv2.createTrackbar(
            "VAdd", self.TRACKWINDOW, 0, 255, lambda value: callback(value, "VAdd")
        )
        cv2.createTrackbar(
            "VSub", self.TRACKWINDOW, 0, 255, lambda value: callback(value, "VSub")
        )

    def apply_hsv_filter(self, original_image):
        hsv = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)

        h, s, v = cv2.split(hsv)
        s = self.shift_channel(s, self.hsv_filter["SAdd"])
        s = self.shift_channel(s, -self.hsv_filter["SSub"])
        v = self.shift_channel(v, self.hsv_filter["VAdd"])
        v = self.shift_channel(v, -self.hsv_filter["VSub"])
        hsv = cv2.merge([h, s, v])

        lower = np.array(
            [self.hsv_filter["HMin"], self.hsv_filter["SMin"], self.hsv_filter["VMin"]]
        )
        upper = np.array(
            [self.hsv_filter["HMax"], self.hsv_filter["SMax"], self.hsv_filter["VMax"]]
        )

        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(hsv, hsv, mask=mask)

        img = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)

        return img

    def shift_channel(self, c, amount):
        if amount > 0:
            lim = 255 - amount
            c[c >= lim] = 255
            c[c < lim] += amount
        elif amount < 0:
            amount = -amount
            lim = amount
            c[c <= lim] = 0
            c[c > lim] -= amount

        return c
