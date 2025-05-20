# app/controllers/side_bar_controller.py
import os
from PySide6.QtCore import QObject, Signal
from app.controllers.file_dialog import select_rnx_file, select_output_dir
from app.models.rinex_extractor import RinexExtractor

class SideBarController(QObject):
    # After setting the input files and output directory, 
    # use the signal to tell MainWindow or Model
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

        # Extract information from submitted .RNX file
        try:
            extractor = RinexExtractor(path)
            result = extractor.extract_rinex_data(path)

            # Update UI fields directly
            self.ui.timeWindowValue.setText(f"{result['start_epoch']} to {result['end_epoch']}")
            self.ui.dataIntervalValue.setText(f"{result['epoch_interval']} s")
            self.ui.receiverTypeValue.setText(result["receiver_type"])
            self.ui.antennaTypeValue.setText(result["antenna_type"])
            self.ui.antennaOffsetValue.setText(", ".join(map(str, result["antenna_offset"])))

            # Fill drop-downs to match values
            self._set_combobox_by_value(self.ui.Receiver_type, result["receiver_type"])
            self._set_combobox_by_value(self.ui.Antenna_type, result["antenna_type"])

            # Logging in terminal to inform user
            self.ui.terminalTextEdit.append(".RNX file metadata extracted and applied to UI fields")

        except Exception as e:
            self.ui.terminalTextEdit.append(f"Error extracting RNX metadata: {e}")
            print(f"Error extracting RNX metadata: {e}")

    def load_output_dir(self):
        path = select_output_dir(self.parent)
        if not path:
            return
        self.output_dir = path
        self.ui.terminalTextEdit.append(f"Output directory selected: {path}")
        self.enable_process_button()

        # If both are ready, emit the ready signal
        if self.rnx_file:
            self.ready.emit(self.rnx_file, self.output_dir)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def enable_process_button(self):
        """Enable the Process button (to be called once prerequisites met).

        Back-end processing logic will be integrated later; for now this is
        simply a convenience wrapper so other components can enable the
        button without touching UI details.
        """
        self.ui.processButton.setEnabled(True)

    def _set_combobox_by_value(self, combo, value: str):
        index = combo.findText(value)
        if index != -1:
            combo.setCurrentIndex(index)

