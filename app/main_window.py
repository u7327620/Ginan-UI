from app.controllers.file_dialog import FileDialogController
from app.views.main_window_ui import Ui_MainWindow
from PySide6.QtWidgets import QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.model = "" # Model empty for now
        self.controller = FileDialogController(self.ui, self.model)