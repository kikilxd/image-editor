from GUI import MainWindow
from PyQt6.QtWidgets import QApplication, QMainWindow
import sys
import logging


app = QApplication(sys.argv)

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) - %(message)s',
    level = logging.DEBUG
)

main_window = MainWindow()
main_window.show()
sys.exit(app.exec())