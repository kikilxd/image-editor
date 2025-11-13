import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QGridLayout, QLineEdit, QPushButton, QComboBox, QSlider


class FilterForm(QDialog):
    def __init__(self, main_window,editor, parent=None):
        logging.debug("initializing filter form")
        super().__init__(parent)
        self.main_window = main_window
        self.editor = editor
        self.setWindowTitle("Add filter")
        self.resize(300,100)
        layout = QGridLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)
        self.combobox = QComboBox(self)
        self.combobox.addItems(["Blur", "Contour", "Detail", "Sharpen"])
        self.combobox.currentTextChanged.connect(self.on_filter_change)
        layout.addWidget(self.combobox, 0, 0)

        self.int_label = QLineEdit("2") #label for selecting blur intensity
        self.intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.intensity_slider.setMinimum(1)
        self.intensity_slider.setMaximum(20)
        self.intensity_slider.setValue(2)


        layout.addWidget(self.int_label, 1, 1, 1, 2)
        layout.addWidget(self.intensity_slider, 1, 0)
        self.intensity_slider.valueChanged.connect(self.update_intensity_qlineedit)

        self.apply_button = QPushButton("Apply Filter")
        self.apply_button.clicked.connect(self.apply_filter)
        layout.addWidget(self.apply_button, 2, 0, 1, 3)

        self.setLayout(layout)
        logging.debug("filter form initialized")

    def update_intensity_qlineedit(self, value):
        self.int_label.setText(str(value))

    def apply_filter(self):
        selected_filter = self.combobox.currentText()
        if selected_filter.lower() == "blur":
            intensity = self.intensity_slider.value()
            logging.debug(f"applying {selected_filter} with intensity {intensity}")
            self.editor.apply_blur(intensity)
        else:
            logging.debug(f"applying {selected_filter} filter")
            self.editor.apply_filter(selected_filter)
        self.main_window.renderImage()

    def on_filter_change(self, value):
        if value.lower() == "blur":
            self.int_label.show()
            self.intensity_slider.show()
        else:
            self.int_label.hide()
            self.intensity_slider.hide()