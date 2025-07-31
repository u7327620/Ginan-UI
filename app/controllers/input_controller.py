# app/controllers/input_controller.py

from __future__ import annotations

import os
from typing import Callable, List

from PySide6.QtCore import QObject, Signal, Qt, QDateTime
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QFileDialog,
    QDialog,
    QFormLayout,
    QDoubleSpinBox,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QDateTimeEdit,
    QInputDialog,
    QMessageBox,
    QComboBox,
)

from app.models.rinex_extractor import RinexExtractor

class InputController(QObject):
    """
    Front-end controller

    Owns all UI input flows:
        - Select RNX file and Output directory
        - Extract RINEX metadata and apply to UI
        - Populate / handle config widgets (Mode, Constellations, etc.)
        - Open small dialogs for selecting some values

    Emits:
        ready(rnx_path: str, output_path: str)

        when both RNX and output dir are set.
    """

    ready = Signal(str, str) # rnx_path, output_path

    def __init__(self, ui, parent_window):
        super().__init__()
        self.ui = ui
        self.parent = parent_window

        self.rnx_file: str = ""
        self.output_dir: str = ""

        ### Wire: file selection buttons ###
        self.ui.observationsButton.clicked.connect(self.load_rnx_file)
        self.ui.outputButton.clicked.connect(self.load_output_dir)

        # Initial states
        self.ui.outputButton.setEnabled(False) # output disabled until RNX chosen
        self.ui.processButton.setEnabled(False) # process enabled later by MainWindow

        ### Bind: configuration drop-downs / UIs ###

        # Single-choice combos (populated on open)
        self._bind_combo(self.ui.Mode, self._get_mode_items)
        self._bind_combo(self.ui.PPP_provider, self._get_ppp_provider_items)
        self._bind_combo(self.ui.PPP_series, self._get_ppp_series_items)

        # Constellations: multi-select with checkboxes, mirror to constellationsValue label
        self._bind_multiselect_combo(
            self.ui.Constellations_2,
            self._get_constellations_items,
            self.ui.constellationsValue,
            placeholder="Constellations",
        )

        # On selection of single-choice combos, mirror value to right-side labels
        self.ui.Mode.activated.connect(
            lambda idx: self._on_select(self.ui.Mode, self.ui.modeValue, "Mode", idx)
        )
        self.ui.Antenna_type.activated.connect(
            lambda idx: self._on_select(self.ui.Antenna_type, self.ui.antennaTypeValue, "Antenna type", idx)
        )
        self.ui.PPP_provider.activated.connect(
            lambda idx: self._on_select(self.ui.PPP_provider, self.ui.pppProviderValue, "PPP provider", idx)
        )
        self.ui.PPP_series.activated.connect(
            lambda idx: self._on_select(self.ui.PPP_series, self.ui.pppSeriesValue, "PPP series", idx)
        )

        # Receiver/Antenna types: allow free-text via popup prompts
        self._enable_free_text_for_receiver_and_antenna()

        # Antenna offset dialog
        self.ui.antennaOffsetButton.clicked.connect(self._open_antenna_offset_dialog)
        self.ui.antennaOffsetButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ui.antennaOffsetValue.setText("0.0, 0.0, 0.0")

        # Time window & Data interval dialogs
        self.ui.timeWindowButton.clicked.connect(self._open_time_window_dialog)
        self.ui.timeWindowButton.setCursor(Qt.CursorShape.PointingHandCursor)

        self.ui.dataIntervalButton.clicked.connect(self._open_data_interval_dialog)
        self.ui.dataIntervalButton.setCursor(Qt.CursorShape.PointingHandCursor)

        # Show-config file chooser. (Does NOT trigger processing.)
        # self.ui.showConfigButton.clicked.connect(self.on_show_config)
        # self.ui.showConfigButton.setCursor(Qt.CursorShape.PointingHandCursor)

    #region File Selection + Metadata Extraction

    def load_rnx_file(self):
        """Pick an RNX file, extract metadata, apply to UI, and enable next steps."""
        path = self._select_rnx_file(self.parent)
        if not path:
            return

        self.rnx_file = path
        self.ui.terminalTextEdit.append(f"RNX selected: {path}")
        self.ui.outputButton.setEnabled(True)  # allow choosing output dir next

        # Extract information from submitted .RNX file and reflect it in the UI
        try:
            extractor = RinexExtractor(path)
            result = extractor.extract_rinex_data(path)

            # Update UI fields directly
            self.ui.constellationsValue.setText(result["constellations"])
            self.ui.timeWindowValue.setText(f"{result['start_epoch']} to {result['end_epoch']}")
            self.ui.dataIntervalValue.setText(f"{result['epoch_interval']} s")
            self.ui.receiverTypeValue.setText(result["receiver_type"])
            self.ui.antennaTypeValue.setText(result["antenna_type"])
            self.ui.antennaOffsetValue.setText(", ".join(map(str, result["antenna_offset"])))

            # Align left-side combos to extracted values where applicable
            self._set_combobox_by_value(self.ui.Receiver_type, result["receiver_type"])
            self._set_combobox_by_value(self.ui.Antenna_type, result["antenna_type"])

            self.ui.terminalTextEdit.append(".RNX file metadata extracted and applied to UI fields")
        except Exception as e:
            self.ui.terminalTextEdit.append(f"Error extracting RNX metadata: {e}")
            print(f"Error extracting RNX metadata: {e}")

        # If both are available already (user might have chosen output first), emit
        if self.rnx_file and self.output_dir:
            self.ready.emit(self.rnx_file, self.output_dir)

    def load_output_dir(self):
        """Pick an output directory; if RNX is also set, emit ready."""
        path = self._select_output_dir(self.parent)
        if not path:
            return

        self.output_dir = path
        self.ui.terminalTextEdit.append(f"Output directory selected: {path}")

        # MainWindow owns when to enable processButton. This controller exposes a helper if needed.
        self.enable_process_button()

        if self.rnx_file:
            self.ready.emit(self.rnx_file, self.output_dir)

    def enable_process_button(self):
        """Public helper so other components can enable the Process button without knowing UI internals."""
        self.ui.processButton.setEnabled(True)

    #endregion

    #region Multi-Selectors Assigning (A.K.A. Combo Plumbing)

    def _on_select(self, combo: QComboBox, label, title: str, index: int):
        """Mirror combo selection to label and reset combo’s placeholder text."""
        value = combo.itemText(index)
        label.setText(value)

        combo.clear()
        combo.addItem(title)

    def _bind_combo(self, combo: QComboBox, items_func: Callable[[], List[str]]):
        """
        Populate a single-choice QComboBox each time it opens.
        Keeps the left combo visually clean while moving the chosen value to the right label.
        """
        combo._old_showPopup = combo.showPopup

        def new_showPopup():
            combo.clear()
            combo.setEditable(True)
            combo.lineEdit().setAlignment(Qt.AlignCenter)
            for item in items_func():
                combo.addItem(item)
            combo.setEditable(False)
            combo._old_showPopup()

        combo.showPopup = new_showPopup

    def _bind_multiselect_combo(
            self,
            combo: QComboBox,
            items_func: Callable[[], List[str]],
            mirror_label,
            placeholder: str,
    ):
        """
        On open, replace the combo’s model with checkbox items and mirror all checked items
        as comma-separated text to mirror_label.
        """
        combo._old_showPopup = combo.showPopup

        def show_popup():
            model = QStandardItemModel(combo)
            for txt in items_func():
                it = QStandardItem(txt)
                it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
                it.setData(Qt.Unchecked, Qt.CheckStateRole)
                model.appendRow(it)

            def on_item_changed(_item: QStandardItem):
                selected = [
                    model.item(r, 0).text()
                    for r in range(model.rowCount())
                    if model.item(r, 0).checkState() == Qt.Checked
                ]
                mirror_label.setText(", ".join(selected) if selected else placeholder)

            model.itemChanged.connect(on_item_changed)
            combo.setModel(model)
            combo._old_showPopup()

        combo.showPopup = show_popup
        combo.clear()
        combo.addItem(placeholder)
        mirror_label.setText(placeholder)

    def _enable_free_text_for_receiver_and_antenna(self):
        """Allow entering custom Receiver/Antenna types via popup prompt."""

        # Receiver type free text
        def _ask_receiver_type():
            text, ok = QInputDialog.getText(self.ui.Receiver_type, "Receiver Type", "Enter receiver type:")
            if ok and text:
                self.ui.Receiver_type.clear()
                self.ui.Receiver_type.addItem(text)
                self.ui.receiverTypeValue.setText(text)

        self.ui.Receiver_type.showPopup = _ask_receiver_type
        self.ui.receiverTypeValue.setText("")

        # Antenna type free text
        def _ask_antenna_type():
            text, ok = QInputDialog.getText(self.ui.Antenna_type, "Antenna Type", "Enter antenna type:")
            if ok and text:
                self.ui.Antenna_type.clear()
                self.ui.Antenna_type.addItem(text)
                self.ui.antennaTypeValue.setText(text)

        self.ui.Antenna_type.showPopup = _ask_antenna_type
        self.ui.antennaTypeValue.setText("")

    #endregion

    #region Small Dialogs

    def _open_antenna_offset_dialog(self):
        dlg = QDialog(self.ui.antennaOffsetButton)
        dlg.setWindowTitle("Antenna Offset")

        # Try to parse existing U, N, E values
        try:
            u0, n0, e0 = [float(x.strip()) for x in self.ui.antennaOffsetValue.text().split(",")]
        except Exception:
            u0 = n0 = e0 = 0.0

        form = QFormLayout(dlg)

        sb_u = QDoubleSpinBox(dlg)
        sb_u.setRange(-9999, 9999)
        sb_u.setDecimals(1)
        sb_u.setValue(u0)
        sb_n = QDoubleSpinBox(dlg)
        sb_n.setRange(-9999, 9999)
        sb_n.setDecimals(1)
        sb_n.setValue(n0)
        sb_e = QDoubleSpinBox(dlg)
        sb_e.setRange(-9999, 9999)
        sb_e.setDecimals(1)
        sb_e.setValue(e0)

        form.addRow("U:", sb_u)
        form.addRow("N:", sb_n)
        form.addRow("E:", sb_e)

        btn_row = QHBoxLayout()
        ok_btn = QPushButton("OK", dlg)
        cancel_btn = QPushButton("Cancel", dlg)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        form.addRow(btn_row)

        ok_btn.clicked.connect(lambda: self._set_antenna_offset(sb_u, sb_n, sb_e, dlg))
        cancel_btn.clicked.connect(dlg.reject)

        dlg.exec()

    def _set_antenna_offset(self, sb_u: QDoubleSpinBox, sb_n: QDoubleSpinBox, sb_e: QDoubleSpinBox, dlg: QDialog):
        u, n, e = sb_u.value(), sb_n.value(), sb_e.value()
        self.ui.antennaOffsetValue.setText(f"{u}, {n}, {e}")
        dlg.accept()

    def _open_time_window_dialog(self):
        dlg = QDialog(self.ui.timeWindowValue)
        dlg.setWindowTitle("Select start / end time")

        vbox = QVBoxLayout(dlg)
        start_edit = QDateTimeEdit(QDateTime.currentDateTime(), dlg)
        end_edit = QDateTimeEdit(QDateTime.currentDateTime(), dlg)

        start_edit.setCalendarPopup(True)
        end_edit.setCalendarPopup(True)
        start_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        end_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")

        vbox.addWidget(start_edit)
        vbox.addWidget(end_edit)

        btn_row = QHBoxLayout()
        ok_btn = QPushButton("OK", dlg)
        cancel_btn = QPushButton("Cancel", dlg)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        vbox.addLayout(btn_row)

        ok_btn.clicked.connect(lambda: self._set_time_window(start_edit, end_edit, dlg))
        cancel_btn.clicked.connect(dlg.reject)

        dlg.exec()

    def _set_time_window(self, start_edit: QDateTimeEdit, end_edit: QDateTimeEdit, dlg: QDialog):
        if end_edit.dateTime() < start_edit.dateTime():
            QMessageBox.warning(dlg, "Time error", "End time cannot be earlier than start time.\nPlease select again.")
            return

        s = start_edit.dateTime().toString("yyyy-MM-dd_HH:mm:ss")
        e = end_edit.dateTime().toString("yyyy-MM-dd_HH:mm:ss")
        self.ui.timeWindowValue.setText(f"{s} to {e}")
        dlg.accept()

    def _open_data_interval_dialog(self):
        val, ok = QInputDialog.getInt(
            self.ui.dataIntervalValue,
            "Data interval",
            "Input interval (seconds):",
            1,
            1,
            999_999,
        )
        if ok:
            # Keep "X s" to match RNX metadata format and existing parsing in MainController
            self.ui.dataIntervalValue.setText(f"{val} s")

    #endregion

    #region "Show Config" Button

    # TODO: Currently opens a file picker? Not meant to do that

    def on_show_config(self):
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select a YAML config file",
            "",
            "YAML files (*.yml *.yaml)",
        )
        if not file_path:
            return

        if not (file_path.endswith(".yml") or file_path.endswith(".yaml")):
            QMessageBox.warning(None, "File format error", "Please select a file ending with .yml or .yaml")
            return

        self.config_path = file_path  # stored for other components if needed

    #endregion

    #region Utility Functions

    @staticmethod
    def _set_combobox_by_value(combo: QComboBox, value: str):
        """Find 'value' in a combo and set it if present."""
        if value is None:
            return
        idx = combo.findText(value)
        if idx != -1:
            combo.setCurrentIndex(idx)

    @staticmethod
    def _select_rnx_file(parent) -> str:
        caption = "Select RINEX File"
        filters = "RINEX Files (*.rnx *.rnx.gz);;All Files (*)"
        path, _ = QFileDialog.getOpenFileName(parent, caption, "", filters)
        return path or ""

    @staticmethod
    def _select_output_dir(parent) -> str:
        """Default to .../app/resources/output if present, else current module dir."""
        system_file_path = os.path.dirname(os.path.abspath(__file__))
        resources_file_path = os.path.normpath(os.path.join(system_file_path, "..", "app", "resources"))
        output_file_path = os.path.join(resources_file_path, "output")

        default_dir = output_file_path if os.path.isdir(output_file_path) else system_file_path
        caption = "Select Output Directory"
        path = QFileDialog.getExistingDirectory(parent, caption, default_dir)
        return path or ""

    #endregion

    #region Statics

    @staticmethod
    def _get_mode_items() -> List[str]:
        return ["Static", "Kinematic", "Dynamic"]

    @staticmethod
    def _get_constellations_items() -> List[str]:
        return ["GPS", "GAL", "GLO", "BDS", "QZS"]

    @staticmethod
    def _get_ppp_provider_items() -> List[str]:
        return ["COD", "GFZ", "JPL", "ESA", "IGS", "WUH"]

    @staticmethod
    def _get_ppp_series_items() -> List[str]:
        return ["RAP", "ULT", "FIN"]

    #endregion