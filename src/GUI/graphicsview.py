from PyQt6.QtWidgets import QRubberBand, QGraphicsView
from PyQt6.QtCore import QRect, QPoint, Qt, QSize
from PyQt6.QtGui import QCursor
import logging


class GraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self.origin = QPoint()
        self.selection_rect = QRect()
        self.selection_mode = False

    def set_selection_mode(self, enabled):
        logging.debug(f"Setting selection mode to {enabled}")
        self.selection_mode = enabled
        self.setInteractive(enabled)
        if enabled:
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def mousePressEvent(self, event):
        if self.selection_mode and event.button() == Qt.MouseButton.LeftButton:
            logging.debug(f"Left button pressed")
            self.origin = event.pos()
            logging.debug(f"Origin: {self.origin}")
            self.rubber_band.setGeometry(QRect(self.origin, QSize()))
            self.rubber_band.show()
            logging.debug(f"showing rubber band")
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.selection_mode and not self.origin.isNull():
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())
        else:
            super().mouseMoveEvent(event)

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