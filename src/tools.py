from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageQt
from PyQt6.QtGui import QPixmap
from PIL.ImageQt import ImageQt

class Editor:
    def __init__(self, path: str = None):
        self.image = None
        self.path = path
        if path:
            self.open(path)

    def open(self, path: str):
        self.image = Image.open(path)
        self.path = path
        return self

    def resize(self, width: int, height: int):
        if self.image:
            self.image = self.image.resize((width, height))
        return self

    def add_text(self, text: str, position=(10, 10), font_size=30, color="white"):
        if not self.image:
            return self

        draw = ImageDraw.Draw(self.image)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except OSError:
            font = ImageFont.load_default()

        draw.text(position, text, fill=color, font=font)
        return self

    def apply_filter(self, filter_name: str):
        if not self.image:
            return self

        filters = {
            "blur": ImageFilter.BLUR,
            "contour": ImageFilter.CONTOUR,
            "detail": ImageFilter.DETAIL,
            "sharpen": ImageFilter.SHARPEN,
        }
        f = filters.get(filter_name.lower())
        if f:
            self.image = self.image.filter(f)
        return self

    def save(self, path: str = None):
        if not self.image:
            return
        save_path = path or self.path
        if save_path:
            self.image.save(save_path)

    def to_qpixmap(self):
        if not self.image:
            return None
        qimage = ImageQt(self.image)
        pixmap = QPixmap.fromImage(qimage)
        return pixmap
