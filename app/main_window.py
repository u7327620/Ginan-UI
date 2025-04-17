from app.controllers.file_dialog import FileDialogController
from app.controllers.history_window import HistoryWindowController
from app.views.main_window_ui import Ui_MainWindow
from PySide6.QtWidgets import QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.models = []
        self.controllers = []
        self.setup_controllers()

    def setup_controllers(self):
        self.controllers.append(FileDialogController(self.ui, "")) # no model for now
        self.controllers.append(HistoryWindowController(self.ui))