from app.views.main_window_ui import Ui_MainWindow
from PySide6.QtWidgets import QFileDialog, QWidget, QVBoxLayout
from app.views.history_window_ui import Ui_HistoryWindow

class FileDialogController:
    def __init__(self, ui:Ui_MainWindow, model): # Model empty for now
        """Directory selector example"""
        self.ui = ui
        self.model = model
        self.setup_file_dialog()

    def setup_file_dialog(self):
        self.ui.inputDataButton.clicked.connect(self.get_directory)
        self.ui.VisualisationButton.clicked.connect(self.open_history_window)

    def get_directory(self):
        dialog = QFileDialog().getExistingDirectory(caption='Select root input directory')
        self.ui.inputPathLineEdit.setText(str(dialog))

    def open_history_window(self):
        for i in reversed(range(self.ui.infoGrid.count())):
            widget_to_remove = self.ui.infoGrid.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)

        self.ui_history_window = Ui_HistoryWindow()
        self.history_widget = QWidget()
        self.ui_history_window.setupUi(self.history_widget)

        self.ui.infoGrid.addWidget(self.history_widget, 0, 0, 1, 2)