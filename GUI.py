from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QAction, QDockWidget, QWidget, QVBoxLayout, QLabel, QApplication
import sys

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.setWindowTitle("Image Editor")
        self.resize(800, 600)
        self.setWindowIcon(QtGui.QIcon())

        self.initsidebar()
        self.initmenubar()
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
        saveAction = QAction("Save", self)
        exitAction = QAction("Exit", self)

        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

