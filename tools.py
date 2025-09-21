from PIL import Image, ImageDraw, ImageFont, ImageFilter

class Editor:
    def __init__(self, path: str):
        self.image = Image.open(path)
    def resize(self, width: int, height: int):
        self.image = self.image.resize(width,height)
        return self
