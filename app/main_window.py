from app.controllers.file_dialog import FileDialogController
from app.views.main_window_ui import Ui_MainWindow
from PySide6.QtWidgets import QMainWindow
from app.controllers.config_controller import ConfigController 

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
        self.controllers.append(ConfigController(self.ui))
      