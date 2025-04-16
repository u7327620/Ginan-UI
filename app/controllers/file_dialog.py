from app.views.main_window_ui import Ui_MainWindow
from PySide6.QtWidgets import QFileDialog

class FileDialogController:
    def __init__(self, ui:Ui_MainWindow, model): # Model empty for now
        """Directory selector example"""
        self.ui = ui
        self.model = model
        self.setup_file_dialog()

    def setup_file_dialog(self):
        self.ui.inputDataButton.clicked.connect(self.get_directory)

    def get_directory(self):
        dialog = QFileDialog().getExistingDirectory(caption='Select root input directory')
        self.ui.inputPathLineEdit.setText(str(dialog))