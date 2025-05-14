from PySide6.QtWidgets import QFileDialog

class FileDialogController:
    def __init__(self, file_dialog_ui, file_requiring_model): # Model empty for now
        """Directory selector example"""
        self.file_dialog_ui = file_dialog_ui
        self.model = file_requiring_model
        self.setup_file_dialog()

    def setup_file_dialog(self):
        self.file_dialog_ui.observationsButton.clicked.connect(self.get_directory)

    def get_directory(self):
        dialog = QFileDialog().getExistingDirectory(caption='Select root input directory')
        self.file_dialog_ui.terminalTextEdit.setText(f"Selected directory: {dialog}")