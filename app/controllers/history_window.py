from PySide6.QtWidgets import QWidget
from app.views.history_window_ui import Ui_HistoryWindow
from app.views.main_window_ui import Ui_MainWindow

class HistoryWindowController:
    def __init__(self, main_window:Ui_MainWindow):
        self.ui_history_window = Ui_HistoryWindow()
        self.history_widget = QWidget()
        self.main_window = main_window
        self.open_history_window()

    def open_history_window(self):
        for i in reversed(range(self.main_window.infoGrid.count())):
            widget_to_remove = self.main_window.infoGrid.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)
        self.main_window.VisualisationButton.clicked.connect(self.open_history_window)
        self.ui_history_window.setupUi(self.history_widget)
        self.main_window.infoGrid.addWidget(self.history_widget, 0, 0, 1, 2)