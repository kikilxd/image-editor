from PIL import Image
from GUI import MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys


app = QApplication(sys.argv)

main_window = MainWindow()
main_window.show()
sys.exit(app.exec_())