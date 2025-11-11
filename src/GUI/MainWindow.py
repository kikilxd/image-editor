import ctypes
import logging
import sys


from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QAction
from PyQt6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QLabel, QApplication,
    QFileDialog, QMessageBox
)

from .FilterForm import FilterForm
from .ResizeForm import ResizeForm
from ..tools import Editor


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        logging.debug("initializing MainWindow")
        super().__init__()
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.setWindowTitle("Image Editor")
        self.resize(800, 600)

        self.editor = Editor()

        self.initsidebar()
        self.initmenubar()
        self.initStatusbar()
        self.initdarktheme()
        self.enable_blur()

        self.image_label = QLabel("Open an image to display")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.image_label)
        logging.debug("initialized MainWindow")


    def enable_blur(self, acrylic=True):
        #DWM blur
        hwnd = int(self.winId())

        class ACCENT_POLICY(ctypes.Structure):
            _fields_ = [
                ("AccentState", ctypes.c_int),
                ("AccentFlags", ctypes.c_int),
                ("GradientColor", ctypes.c_int),
                ("AnimationId", ctypes.c_int),
            ]
        class MARGINS(ctypes.Structure):
            _fields_ = [
                ("cxLeftWidth", ctypes.c_int),
                ("cxRightWidth", ctypes.c_int),
                ("cxTopWidth", ctypes.c_int),
                ("cxBottomWidth", ctypes.c_int),
            ]

        # https://learn.microsoft.com/en-us/windows/win32/dwm/windowcompositionattribdata
        class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
            _fields_ = [
                ("Attribute", ctypes.c_int),
                ("Data", ctypes.c_void_p),
                ("SizeOfData", ctypes.c_size_t),
            ]

        ACCENT_ENABLE_BLURBEHIND = 3
        ACCENT_ENABLE_ACRYLICBLURBEHIND = 4


        accent = ACCENT_POLICY()
        accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND if acrylic else ACCENT_ENABLE_BLURBEHIND
        accent.AccentFlags = 0
        # ARGB (alpha, red, green, blue) → 0xAARRGGBB
        # use low alpha (~0x10) for subtle tint
        accent.GradientColor = 0x10000000
        accent.AnimationId = 0

        # https://learn.microsoft.com/en-us/windows/win32/api/uxtheme/ns-uxtheme-margins
        margins = MARGINS()
        margins.cxLeftWidth = 5
        margins.cxRightWidth = 5
        margins.cxTopWidth = 5
        margins.cxBottomWidth = 5

        # https://learn.microsoft.com/en-us/windows/win32/dwm/windowcompositionattribdata
        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = 19  # WCA_ACCENT_POLICY
        data.SizeOfData = ctypes.sizeof(accent)
        data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.c_void_p)

        # https://learn.microsoft.com/en-us/windows/win32/dwm/blur-ovw
        ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(margins))


        # https://learn.microsoft.com/en-us/windows/win32/dwm/setwindowcompositionattribute
        set_window_composition_attribute = ctypes.windll.user32.SetWindowCompositionAttribute
        set_window_composition_attribute(hwnd, ctypes.byref(data))
        self.setStyleSheet("""
        QMainWindow {
            background: transparent;
        }
        * {
            background: transparent;
        }
        """)
    def initsidebar(self):
        sidebar = QDockWidget("Tools", self)
        sidebar.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        sidebar.setTitleBarWidget(QWidget())  # hide title bar

        sidebar.setStyleSheet("""
                QDockWidget {
                    background: transparent;
                }
            """)

        # Sidebar content
        sidebarContent = QWidget()
        layout = QVBoxLayout()
        label = QLabel("Tools")
        label.setStyleSheet("color: white; font-size: 16px;")
        layout.addWidget(label)
        layout.addStretch()
        sidebarContent.setLayout(layout)

        sidebar.setWidget(sidebarContent)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, sidebar)
        logging.debug("initialized sidebar")

    def initmenubar(self):
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        menubar.setStyleSheet("""
        QMenuBar {
        background: transparent;
        border-radius: 8px;
        }
        """)
        fileMenu = menubar.addMenu("File")
        filterMenu = menubar.addMenu("Filters")

        openAction = QAction("Open", self)
        openAction.triggered.connect(self.openImage) # type: ignore # pycharm doesn't like that line, so I had to silence it

        saveAction = QAction("Save", self)
        saveAction.triggered.connect(self.saveImage) # type: ignore

        resizeAction = QAction("Resize", self)
        resizeAction.triggered.connect(self.showResizeForm) # type: ignore

        FilterFormAction = QAction("FilterForm", self)
        FilterFormAction.triggered.connect(self.showFilterForm) # type: ignore

        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(resizeAction)
        fileMenu.addSeparator()
        fileMenu.addAction("Exit", self.close)
        filterMenu.addAction(FilterFormAction)
        logging.debug("initialized menubar")

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
            scaled = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)

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
