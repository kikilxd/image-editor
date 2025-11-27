import logging

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageQt
from PIL.ImageFilter import GaussianBlur
from PyQt6.QtGui import QPixmap
from PIL.ImageQt import ImageQt

class Editor:
    def __init__(self, path: str = None):
        self.image = None
        self.path = path
        # list of PIL.Image objects/snapshots of states
        self._history = []
        self._history_index = -1
        self._history_limit = 20 # max number of states to keep in history
        if path:
            self.open(path)

    def _push_history(self):
        # append a snapshot of the image to history.
        # Maintains the linear undo/redo behavior: truncates any redo history when new state is added.

        if not self.image:
            return
        # magic trick
        if self._history_index < len(self._history) - 1:
            self._history = self._history[: self._history_index + 1]
        # store a copy to avoid accidental shared-state mutation
        try:
            snapshot = self.image.copy()
        except Exception:
            # fallback:: create a new image from bytes
            snapshot = self.image
        self._history.append(snapshot)

        # cut history if it grows too large
        while len(self._history) > self._history_limit:
            self._history.pop(0)
        self._history_index = len(self._history) - 1

    def can_undo(self) -> bool:
        return self._history_index > 0

    def can_redo(self) -> bool:
        # checks if there is snapshot before the current image state
        return self._history_index < len(self._history) - 1

    def undo(self) -> bool:
        if not self.can_undo():
            logging.debug("undo: nothing to undo")
            return False
        self._history_index -= 1
        # use a copy so that future mutations don't alter stored snapshot
        self.image = self._history[self._history_index].copy()
        logging.debug(f"undo: moved to history index {self._history_index}")
        return True

    def redo(self) -> bool:
        if not self.can_redo():
            logging.debug("redo: nothing to redo")
            return False
        self._history_index += 1
        self.image = self._history[self._history_index].copy()
        logging.debug(f"redo: moved to history index {self._history_index}")
        return True

    def open(self, path: str):
        logging.debug(f"opening image: {path}")
        self.image = Image.open(path)
        self.path = path
        # initialize history with the opened image state
        self._history = []
        self._history_index = -1
        self._push_history()
        return self

    def resize(self, width: int, height: int):
        logging.debug(f"called resize function: {width}, {height}")
        if self.image:
            self.image = self.image.resize((width, height))
            # push new state after mutation
            self._push_history()
        return self

    def add_text(self, text: str, position, font_size=40, color="white"):
        if not self.image:
            logging.debug("add text: no image")
            return self

        draw = ImageDraw.Draw(self.image)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except OSError:
            font = ImageFont.load_default()

        draw.text(position, text, fill=color, font=font)
        logging.debug(f"Text '{text}' added at {position}")
        # push new state after mutation
        self._push_history()
        return self

    def apply_blur(self, intensity: int):
        if not self.image:
            logging.debug("apply_blur called without image")
            return self
        logging.debug(f"apply_blur: {intensity}")
        self.image = self.image.filter(GaussianBlur(radius=intensity))
        # push new state after mutation
        self._push_history()
        return self


    def apply_filter(self, filter_name: str):
        if not self.image:
            logging.debug("apply_filter called without image")
            return self
        logging.debug(f"apply_filter: {filter_name}")
        filters = {
            "contour": ImageFilter.CONTOUR,
            "detail": ImageFilter.DETAIL,
            "sharpen": ImageFilter.SHARPEN,
        }
        f = filters.get(filter_name.lower())
        if f:
            logging.debug(f"setting {f} filter")
            self.image = self.image.filter(f)
            # push new state after mutation
            self._push_history()
        return self


    def save(self, path: str = None):
        logging.debug(f"saving image: {path}")
        if not self.image:
            logging.debug("save called, but self.image is None")
            return
        save_path = path or self.path
        if save_path:
            self.image.save(save_path)
            logging.debug(f"saved image: {save_path}")

    def to_qpixmap(self):
        logging.debug("converting image to QPixmap")
        if not self.image:
            logging.error("to_qpixmap called, but self.image is None")
            return None

        # avoiding mutating self.image, using a temporary copy
        img_for_qt = self.image
        if img_for_qt.mode not in ("RGB", "RGBA"):
            logging.debug("converting image mode from %s to RGBA", img_for_qt.mode)
            img_for_qt = img_for_qt.convert("RGBA")

        qimage = ImageQt(img_for_qt)
        # keep a reference to the qimage to avoid being thrown into shit pile by garbage collector while Qt uses it
        self._qimage_ref = qimage

        pixmap = QPixmap.fromImage(qimage)
        logging.debug("qimage: %s", qimage)
        logging.debug("pixmap: %s", pixmap)

        return pixmap
