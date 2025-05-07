from app.controllers.file_dialog import FileDialogController
from app.views.main_window_ui import Ui_MainWindow
from PySide6.QtWidgets import QMainWindow
from app.controllers.config_controller import ConfigController 
from PySide6.QtWidgets import QMessageBox, QFileDialog
from datetime import datetime


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
        self.ui.processButton.clicked.connect(self.on_run_pea)
        self.ui.showConfigButton.clicked.connect(self.on_show_config)

    
    def on_show_config(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a YAML config file",  
            "",                            
            "YAML files (*.yml *.yaml)"    
        )
        if not file_path:
            return

        # Verify the file suffix is .yml or .yaml
        if not (file_path.endswith(".yml") or file_path.endswith(".yaml")):
            QMessageBox.warning(
                self,
                "File format error",
                "Please select a file ending with .yml or .yaml"
            )
            return

        # Save the valid config path for later use
        self.config_path = file_path


    def on_run_pea(self):
        raw_text = self.ui.Time_window.text()
        normalized = raw_text.replace("_", " ")
        try:
            start_str, end_str = normalized.split("→")
            start = datetime.strptime(start_str.strip(), "%Y-%m-%d %H:%M:%S")
            end   = datetime.strptime(end_str.strip(),   "%Y-%m-%d %H:%M:%S")
        except Exception:
            QMessageBox.warning(
                self,
                "Format error",
                "Time window must be in the format:\n"
                "YYYY-MM-DD HH:MM:SS → YYYY-MM-DD HH:MM:SS"
            )
            return

        if start > end:
            QMessageBox.warning(
                self,
                "Time error",
                "Start time cannot be later than end time. Please correct it."
            )
            return

        if not getattr(self, "config_path", None):
            QMessageBox.warning(
                self,
                "No config file",
                "Please click Show config and select a YAML file first."
            )
            return

        self.ui.peaOutputTerminal.clear()
        self.ui.peaOutputTerminal.appendPlainText(
            "Basic validation passed, starting PEA execution..."
        )
    

    
        
    