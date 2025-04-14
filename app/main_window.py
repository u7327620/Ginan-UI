from PySide6 import QtWidgets
import sys

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PySide6 init")
        label = QtWidgets.QLabel("Initial label")
        label.setMargin(10)
        self.setCentralWidget(label)
        self.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.exec()