import sys
from PySide6.QtWidgets import QApplication
from app.main_window import MainWindow
from utils.helpers import compile_ui

if __name__ == "__main__":
    app = QApplication(sys.argv)
    compile_ui()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())