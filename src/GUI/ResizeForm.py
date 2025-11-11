import logging
from PyQt6.QtWidgets import QDialog, QGridLayout, QLineEdit, QPushButton, QLabel

class ResizeForm(QDialog):
    def __init__(self, parent=None):
        logging.debug("initializing resize form")
        super().__init__(parent)
        self.setWindowTitle("Resize Image")
        grid = QGridLayout()
        grid.addWidget(QLabel("New Width:"), 0, 0)
        self.width_input = QLineEdit()
        grid.addWidget(self.width_input, 0, 1)

        grid.addWidget(QLabel("New Height:"), 1, 0)
        self.height_input = QLineEdit()
        grid.addWidget(self.height_input, 1, 1)

        self.button = QPushButton("Resize")
        grid.addWidget(self.button, 2, 0, 1, 2)
        self.setLayout(grid)
        logging.debug("resize form initialized")