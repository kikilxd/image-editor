from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QPixmap
from PyQt5.QtWidgets import QAction, QDockWidget, QWidget, QVBoxLayout, QLabel, QApplication, QFileDialog
import sys

class ResizeForm(QDialog):
    def __init__(self, parent=None):
        super(ResizeForm, self).__init__(parent)
        grid = QGridLayout()

        grid.addWidget(QLabel("Old"), 0, 1)
        grid.addWidget(QLabel("New"), 0, 2)

        grid.addWidget(QLabel("X"), 1, 0)
        grid.addWidget(QLineEdit(), 1, 1)
        grid.addWidget(QLineEdit(), 1, 2)

        grid.addWidget(QLabel("Y"), 2, 0)
        grid.addWidget(QLineEdit(), 2, 1)
        grid.addWidget(QLineEdit(), 2, 2)

        button = QPushButton("Resize")

        main_layout = QVBoxLayout()
        main_layout.addLayout(grid)
        main_layout.addWidget(button)

        self.setLayout(main_layout)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.setWindowTitle("Image Editor")
        self.resize(800, 600)
        self.setWindowIcon(QtGui.QIcon())

        self.initsidebar()
        self.initmenubar()
        self.initdarktheme()
        self.image_label = QLabel("Open an image to display")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.image_label)

    def initsidebar(self):
        sidebar = QDockWidget("Tools", self)
        sidebar.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        sidebarContent = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("sidebar ph"))
        layout.addWidget(QLabel("button1"))
        layout.addWidget(QLabel("button2"))

        layout.addStretch()
        sidebarContent.setLayout(layout)
        sidebar.setWidget(sidebarContent)
        self.addDockWidget(Qt.LeftDockWidgetArea, sidebar)

    def initmenubar(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("File")

        openAction = QAction("Open", self)
        openAction.triggered.connect(lambda: self.openImage(self.image_label))
        saveAction = QAction("Save", self)
        exitAction = QAction("Exit", self)

        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

    def initdarktheme(self):
        self.app.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(18, 18, 18))
        palette.setColor(QPalette.WindowText, QColor(230, 230, 230))
        palette.setColor(QPalette.Base, QColor(28, 28, 28))
        palette.setColor(QPalette.AlternateBase, QColor(38, 38, 38))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(230, 230, 230))
        palette.setColor(QPalette.Button, QColor(33, 33, 33))
        palette.setColor(QPalette.ButtonText, QColor(230, 230, 230))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Highlight, QColor(66, 133, 244))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        self.app.setPalette(palette)

    def renderimage(self, imageLabel: QLabel, imagePath: str):
        pixmap = QPixmap(imagePath)
        if pixmap.isNull():
            print("Failed to load image")
            return

        scaledPixmap = pixmap.scaled(
            imageLabel.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        imageLabel.setPixmap(scaledPixmap)

    def openImage(self, imageLabel: QLabel):
        path, _ = QFileDialog.getOpenFileName(
            imageLabel, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            self.renderimage(imageLabel, path)