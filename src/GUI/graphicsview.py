from PyQt6.QtWidgets import QRubberBand, QGraphicsView
from PyQt6.QtCore import QRect, QPoint, Qt, QSize
from PyQt6.QtGui import QCursor

class GraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self.origin = QPoint()
        self.selection_rect = QRect()
        self.selection_mode = False

    def set_selection_mode(self, enabled):
        self.selection_mode = enabled
        self.setInteractive(enabled)
        if enabled:
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def mousePressEvent(self, event):
        if self.selection_mode and event.button() == Qt.MouseButton.LeftButton:
            self.origin = event.pos()
            self.rubber_band.setGeometry(QRect(self.origin, QSize()))
            self.rubber_band.show()
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
            viewport_rect = QRect(self.origin, event.pos()).normalized()
            if viewport_rect.isEmpty():
                self.set_selection_mode(False)
                return
            scene_rect = self.mapToScene(viewport_rect).boundingRect()
            rect_int = scene_rect.toRect()
            if rect_int.isEmpty():
                self.set_selection_mode(False)
                return
            parent = self.parent()
            if parent and hasattr(parent, 'handle_selection'):
                parent.handle_selection(rect_int)

            self.set_selection_mode(False)
        else:
            super().mouseReleaseEvent(event)