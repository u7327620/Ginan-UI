from app.views.main_window_ui import Ui_MainWindow
from PySide6.QtWidgets import QFileDialog

class FileDialogController:
    def __init__(self, file_dialog_ui: Ui_MainWindow, file_requiring_model=None):
        self.ui = file_dialog_ui
        self.model = file_requiring_model
        self.setup_file_dialog()

    def setup_file_dialog(self):
        self.ui.observationsButton.clicked.connect(self.open_file_dialog)

    def open_file_dialog(self):
        filters = "HTML Files (*.html)" # only .html
        file_path, _ = QFileDialog.getOpenFileName(
            self.ui,                     
            "Select Observations File", 
            "",                        
            filters                     
        )
        if file_path:
            self.ui.terminalTextEdit.append(f"Selected file: {file_path}")
            # TODO: pass the file_path to backend or model
            # e.g. self.model.observations_file = file_path
            # or call Process button:
            # self.ui.processButton.setEnabled(True)
