from PyQt6.QtWidgets import QRubberBand, QGraphicsView, QGraphicsTextItem
from PyQt6.QtCore import QRect, QPoint, Qt
from PyQt6.QtGui import QCursor, QColor, QFont
import logging


class GraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self.origin = QPoint()
        self.selection_rect = QRect()
        self.selection_mode = False
        self.placing_text = None
        self.place_text_font = None
        self.text_color = QColor(230,230,230)

    def set_selection_mode(self, enabled):
        logging.debug(f"Setting selection mode to {enabled}")
        self.selection_mode = enabled
        self.setInteractive(enabled)
        if enabled:
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def mousePressEvent(self, event):
        if self.placing_text and event.button() == Qt.MouseButton.LeftButton:
            try:
                scene_point = self.mapToScene(event.position().toPoint())
            except Exception:
                scene_point = self.mapToScene(event.pos())

            text_item = QGraphicsTextItem(self.placing_text)
            if self.place_text_font:
                text_item.setFont(self.place_text_font)
            text_item.setDefaultTextColor(self.text_color)
            text_item.setPos(scene_point)
            scene = self.scene()
            if scene:
                scene.addItem(text_item)

            parent = self.parent()
            try:
                if hasattr(parent, "editor"):
                    editor = parent.editor
                    if hasattr(editor, "draw_text"):
                        editor.draw_text(scene_point.x(), scene_point.y(), self.placing_text, self.place_text_font, self.text_color)
                        if hasattr(parent, "renderImage"):
                            parent.renderImage()
                    # fallback to Editor.add_text (existing tools.Editor) which expects (text, position, font_size, color)
                    elif hasattr(editor, "add_text"):
                        # convert font to point size
                        font_size = None
                        if self.place_text_font:
                            try:
                                font_size = int(self.place_text_font.pointSize())
                            except Exception:
                                font_size = None
                        if not font_size:
                            font_size = 40
                        # convert QColor to RGB tuple or string
                        col = self.text_color
                        try:
                            # QColor.getRgb returns (r,g,b,a)
                            r, g, b, a = col.getRgb()
                            color_rgb = (r, g, b)
                        except Exception:
                            color_rgb = "white"
                        editor.add_text(self.placing_text, (int(scene_point.x()), int(scene_point.y())), font_size, color_rgb)
                        if hasattr(parent, "renderImage"):
                            parent.renderImage()
            except Exception:
                pass

            # exit place-text mode
            self.placing_text = None
            self.place_text_font = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            return

        # default behavior
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.selection_mode and not self.origin.isNull():
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())
        else:
            super().mouseMoveEvent(event)


    def set_place_text(self, text: str, font: QFont | None = None, color: QColor | None = None):
        if not text:
            return
        # set attributes consistently
        self.placing_text = text
        if font is not None:
            self.place_text_font = font
        if color is not None:
            self.text_color = color
        self.setCursor(Qt.CursorShape.IBeamCursor)

    def mouseReleaseEvent(self, event):
        if self.selection_mode and event.button() == Qt.MouseButton.LeftButton:
            self.rubber_band.hide()
            logging.debug(f"left button released")
            logging.debug(f"Hide rubber band")
            viewport_rect = QRect(self.origin, event.pos()).normalized()
            logging.debug(f"created viewport rect: startpos: {self.origin}, endpos: {event.pos()}")

            if self.origin == event.pos(): # handles click without dragging
                logging.debug(f"set selection mode to False because self.origin == event.pos()")
                self.set_selection_mode(False)
                return
            scene_rect = self.mapToScene(viewport_rect).boundingRect() # convertion to scene
            logging.debug(f"scene rect: {scene_rect}")
            rect_int = scene_rect.toRect() # pillow compatibility shit
            logging.debug(f"rect int: {rect_int}")
            if rect_int.isEmpty():
                self.set_selection_mode(False)
                logging.debug(f"set selection mode to False because rect_int is empty")
                return
            parent = self.parent()
            if parent and hasattr(parent, 'handle_selection'):
                parent.handle_selection(rect_int)

            self.set_selection_mode(False)
        else:
            super().mouseReleaseEvent(event)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape and self.selection_mode:
            self.rubber_band.hide()
            self.set_selection_mode(False)
            logging.debug("Selection cancelled by ESC")
        else:
            super().keyPressEvent(event)
