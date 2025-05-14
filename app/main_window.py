from app.controllers.file_dialog import FileDialogController
from PySide6.QtWidgets import QMainWindow
from app.controllers.config_controller import ConfigController
from utils.helpers import compile_ui


def setup_main_window():
    try :
        from app.views.main_window_ui import Ui_MainWindow
    except ModuleNotFoundError:
        compile_ui()
        print("Compiled ui, re import")
        from app.views.main_window_ui import Ui_MainWindow
    window = Ui_MainWindow()
    return window


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = setup_main_window()
        self.ui.setupUi(self)
        self.models = []
        self.controllers = []
        self.setup_controllers()

    def setup_controllers(self):
        self.controllers.append(FileDialogController(self.ui, "")) # no model for now
        self.controllers.append(ConfigController(self.ui))
      