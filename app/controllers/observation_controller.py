# app/controllers/observation_controller.py
import os
from PySide6.QtCore import QObject, Signal
from app.controllers.file_dialog import select_rnx_file, select_output_dir

class ObservationController(QObject):
    # After setting the two files, use the signal to tell MainWindow or Model
    ready = Signal(str, str)   # rnx_path, output_path

    def __init__(self, ui, parent_window):
        super().__init__()
        self.ui = ui
        self.parent = parent_window
        self.rnx_file = ""
        self.output_dir = ""

        # wire UI buttons to handler methods
        self.ui.observationsButton.clicked.connect(self.load_rnx_file)
        self.ui.outputButton.clicked.connect(self.load_output_dir)

        # initial state: only Observations button is active
        self.ui.outputButton.setEnabled(False)
        self.ui.processButton.setEnabled(False)

        # When everything is ready, processButton is connected to the subsequent controller or model

    # ---------- private slots ----------
    def load_rnx_file(self):
        path = select_rnx_file(self.parent)
        if not path:
            return
        self.rnx_file = path
        self.ui.terminalTextEdit.append(f"RNX selected: {path}")
        self.ui.outputButton.setEnabled(True)

    def load_output_dir(self):
        path = select_output_dir(self.parent)
        if not path:
            return
        default_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "example", "output"))
        if os.path.commonpath([default_dir, path]) != default_dir:
            self.ui.terminalTextEdit.append("Please select a directory inside example/output")
            return

        self.output_dir = path
        self.ui.terminalTextEdit.append(f"Output directory: {path}")
        self.ui.outputButton.setText(os.path.basename(path))
        self.ui.processButton.setEnabled(True)

        # If both are ready, emit the ready signal
        if self.rnx_file:
            self.ready.emit(self.rnx_file, self.output_dir)



