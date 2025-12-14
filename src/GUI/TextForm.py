from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QSpinBox, QPushButton

class TextInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add text to image")
        self.resize(300, 150)

        layout = QVBoxLayout()
        form = QFormLayout()

        self.text_input = QLineEdit("")
        self.size_input = QSpinBox()
        self.size_input.setRange(8, 200)
        self.size_input.setValue(40)
        form.addRow("Text:", self.text_input)
        form.addRow("Font Size:", self.size_input)
        layout.addLayout(form)
        ok_btn = QPushButton("OK – Click on Image")
        ok_btn.clicked.connect(self.accept)
        self.button = ok_btn
        layout.addWidget(ok_btn)
        self.setLayout(layout)