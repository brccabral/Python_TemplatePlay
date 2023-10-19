from abc import ABC, abstractmethod


class WindowCaptureABC(ABC):
    @abstractmethod
    def screenshot(self):
        raise Exception("not implemented")
