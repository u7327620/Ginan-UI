# app/controllers/file_dialog.py

from app.views.main_window_ui import Ui_MainWindow
from PySide6.QtWidgets           import QFileDialog
import os

class FileDialogController:
    def __init__(self, ui: Ui_MainWindow, model=None):
        self.ui    = ui
        self.model = model

        self.rnx_file = None
        self.pos_file = None

        self.ui.processButton.setEnabled(False)

        self.ui.observationsButton.clicked.connect(self.select_rnx_file)
        self.ui.outputButton.clicked.connect(self.select_pos_file)
        self.ui.processButton.clicked.connect(self.process_and_display)

    def select_rnx_file(self):
        path, _ = QFileDialog.getOpenFileName(
            parent=None,
            caption="Select Observations File (.rnx)",
            dir=os.getcwd(),
            filter="RINEX Files (*.rnx)"
        )
        if not path:
            return
        self.rnx_file = path
        self.ui.terminalTextEdit.append(f"Selected RINEX file: {path}")
        self._try_enable_process()

    def select_pos_file(self):
        path, _ = QFileDialog.getOpenFileName(
            parent=None,
            caption="Select Output POS File (.pos)",
            dir=os.getcwd(),
            filter="POS Files (*.pos)"
        )
        if not path:
            return
        self.pos_file = path
        self.ui.terminalTextEdit.append(f"Selected POS file: {path}")
        self._try_enable_process()

    def _try_enable_process(self):
        if self.rnx_file and self.pos_file:
            self.ui.processButton.setEnabled(True)

    def process_and_display(self):
        html_path, _ = QFileDialog.getOpenFileName(
            parent=None,
            caption="Select HTML File to Display",
            dir=os.getcwd(),
            filter="HTML Files (*.html)"
        )
        if not html_path:
            self.ui.terminalTextEdit.append("No HTML file selected.")
            return

        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.ui.visualisationTextEdit.setHtml(html)
        self.ui.terminalTextEdit.append("The selected HTML file is displayed.")
