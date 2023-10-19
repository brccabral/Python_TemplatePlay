import cv2


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
        return self.img_cv2.shape[1]

    @property
    def height(self):
        return self.img_cv2.shape[0]
