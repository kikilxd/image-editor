import logging
import sys

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QAction
from PyQt6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QLabel, QApplication,
    QFileDialog, QMessageBox, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QPushButton
)

from .FilterForm import FilterForm
from .ResizeForm import ResizeForm
from ..tools import Editor
from .graphicsview import GraphicsView
from .TextForm import TextInputDialog

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        logging.debug("initializing MainWindow")
        super().__init__()
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.setWindowTitle("Image Editor")
        self.resize(800, 600)

        self.editor = Editor()



        self.scene = QGraphicsScene()
        logging.debug(f"scene: {self.scene}")

        self.view = GraphicsView(self.scene, self)
        logging.debug(f"view: {self.view}")

        self.view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.view)

        self.initsidebar()
        self.initmenubar()
        self.initdarktheme()
        self.initStatusbar()

        logging.debug("initialized MainWindow")
        self.image_item = None

    def initsidebar(self):
        sidebar = QDockWidget("Tools", self)
        sidebar.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        sidebarContent = QWidget()
        layout = QVBoxLayout()
        sidebar.setStyleSheet("""
        QPushButton{
            height: 80px;
            background-color: #121212;
            }""")
        resizebutton = QPushButton("Resize")
        resizebutton.clicked.connect(self.showResizeForm)
        layout.addWidget(resizebutton)
        filterbutton = QPushButton("Filter")
        filterbutton.clicked.connect(self.showFilterForm)
        layout.addWidget(filterbutton)
        textbutton = QPushButton("Text")
        textbutton.clicked.connect(self.showTextForm)
        layout.addWidget(textbutton)
        layout.addStretch()
        sidebarContent.setLayout(layout)
        sidebar.setWidget(sidebarContent)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, sidebar)
        logging.debug("initialized sidebar")

    def initmenubar(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("File")
        EditMenu = menubar.addMenu("Edit")

        openAction = QAction("Open", self)
        openAction.triggered.connect(self.openImage) # type: ignore # pycharm doesn't like that line, so I had to silence it

        saveAction = QAction("Save", self)
        saveAction.triggered.connect(self.saveImage) # type: ignore

        resizeAction = QAction("Resize", self)
        resizeAction.triggered.connect(self.showResizeForm) # type: ignore

        FilterFormAction = QAction("Add filter", self)
        FilterFormAction.triggered.connect(self.showFilterForm) # type: ignore

        selectionAction = QAction("Selection", self)
        selectionAction.triggered.connect(lambda x: self.view.set_selection_mode(True))

        AddTextAction = QAction("Add text", self)
        AddTextAction.triggered.connect(self.showTextForm)

        self.undoAction = QAction("Undo", self)
        self.undoAction.setShortcut("Ctrl+Z")
        self.undoAction.triggered.connect(self.undo)

        self.redoAction = QAction("Redo", self)
        self.redoAction.setShortcut("Ctrl+Y")
        self.redoAction.triggered.connect(self.redo)

        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addSeparator()
        fileMenu.addAction("Exit", self.close)
        EditMenu.addAction(FilterFormAction)
        EditMenu.addAction(resizeAction)
        EditMenu.addAction(selectionAction)
        EditMenu.addAction(AddTextAction)
        EditMenu.addSeparator()
        EditMenu.addAction(self.undoAction)
        EditMenu.addAction(self.redoAction)
        logging.debug("initialized menubar")

        # ensure actions reflect current editor state
        self.update_undo_redo_actions()

    def initdarktheme(self):
        self.app.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(18, 18, 18))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(230, 230, 230))
        palette.setColor(QPalette.ColorRole.Base, QColor(28, 28, 28))
        palette.setColor(QPalette.ColorRole.Text, QColor(230, 230, 230))
        palette.setColor(QPalette.ColorRole.Button, QColor(33, 33, 33))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(230, 230, 230))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(66, 133, 244))
        self.app.setPalette(palette)
        logging.debug("dark theme applied")

    def openImage(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.path_label.setText(path)
            self.editor.open(path)
            self.renderImage()

    def renderImage(self):
        logging.debug("rendering image")
        pixmap = self.editor.to_qpixmap()
        if pixmap:
            self.scene.clear()
            self.image_item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(self.image_item)
            self.view.fitInView(self.image_item, Qt.AspectRatioMode.KeepAspectRatio)
        # update undo/redo action states after any render (which follows edits)
        self.update_undo_redo_actions()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image_item is not None and  not self.image_item.pixmap().isNull():
            self.view.fitInView(self.image_item, Qt.AspectRatioMode.KeepAspectRatio)

    def showResizeForm(self):
        if not self.editor.image:
            QMessageBox.warning(self, "No Image", "Open an image first")
            return

        form = ResizeForm(self)
        form.button.clicked.connect(lambda: self.applyResize(form))
        form.show()

    def showFilterForm(self):
        if not self.editor.image:
            QMessageBox.warning(self, "No Image", "Open an image first")
            return

        form = FilterForm(main_window=self, parent=self, editor=self.editor)
        form.show()

    def showTextForm(self):
        if not self.editor.image:
            QMessageBox.warning(self, "No Image", "Open an image first")
            return

        form = TextInputDialog(parent=self)
        form.show()

    def applyResize(self, form):
        try:
            w = int(form.width_input.text())
            h = int(form.height_input.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid width or height")
            return

        self.editor.resize(w, h)
        self.renderImage()
        form.close()

    def initStatusbar(self):
        self.status_bar = self.statusBar()
        self.path_label = QLabel("Image not loaded")
        self.status_bar.addPermanentWidget(self.path_label)

    def saveImage(self):
        if not self.editor.image:
            QMessageBox.warning(self, "No Image", "Open an image first")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.editor.save(path)
            QMessageBox.information(self, "Saved", f"Saved to: {path}")

    # undo/redo helpers
    def update_undo_redo_actions(self):
        try:
            can_undo = self.editor.can_undo()
            can_redo = self.editor.can_redo()
        except Exception:
            can_undo = False
            can_redo = False
        self.undoAction.setEnabled(can_undo)
        self.redoAction.setEnabled(can_redo)

    def undo(self):
        if self.editor.undo():
            self.renderImage()

    def redo(self):
        if self.editor.redo():
            self.renderImage()
