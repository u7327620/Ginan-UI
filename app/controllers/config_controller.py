"""
This controller encapsulates all logic related to populating and managing the configuration drop-down menus (QComboBox) in the main UI.

1. Separation of Concerns:
   - All combo box setup and data sourcing lives here, not in MainWindow or UI definitions.
2. View–Logic Decoupling:
   - UI (.ui) only defines layout and widgets.
   - Controller handles dynamic data binding and interactions.
3. Extensibility & Reuse:
   - New panels or dropdowns can be added in separate controllers without bloating a single file.
4. Testability:
   - ConfigController can be instantiated with a mock Ui_MainWindow to verify menu items or simulate user interactions.
"""
import os
from datetime import datetime

from PySide6.QtCore import Qt, QUrl, QDate, QDateTime
from PySide6.QtGui import QDesktopServices, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QDoubleSpinBox,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QCalendarWidget,
    QDateTimeEdit,
    QInputDialog,
    QMessageBox,
    QFileDialog,
)


class ConfigController:
    def __init__(self, ui):
        self.ui = ui

        # —— Show config & Run PEA —— #
        self.default_config_path = "app/resources/Yaml/default_config.yaml"
        self.ui.showConfigButton.clicked.connect(self.on_show_config)
        self.ui.processButton.clicked.connect(self.on_run_pea)       

        # bond up QComboBox's showPopup
        self._bind_combo(self.ui.Mode, self._get_mode_items)
        self._bind_combo(self.ui.PPP_provider, self._get_ppp_provider_items)
        self._bind_combo(self.ui.PPP_series, self._get_ppp_series_items)

        # Multiple Choice Binding
        combo = self.ui.Constellations_2
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.NoInsert)
        combo.lineEdit().setReadOnly(True)
        self._bind_multiselect_combo(combo,
                                     self._get_constellations_items,
                                     combo.lineEdit(), #The results are written directly here
                                     placeholder="Select one or more") # Prompt to select one or more


        # Time window：Start & End Date & Time
        self.ui.timeWindowButton.clicked.connect(self._open_time_window_dialog)
        self.ui.timeWindowButton.setCursor(Qt.PointingHandCursor)

        # Data interval：set seconds
        self.ui.dataIntervalButton.clicked.connect(self._open_data_interval_dialog)
        self.ui.dataIntervalButton.setCursor(Qt.PointingHandCursor)

        # Show config: Click the button to open the editor
        # self.ui.showConfigButton.clicked.connect(self.on_show_config) #comment out for now, because it would active the button repeatedly
        self.ui.showConfigButton.setCursor(Qt.PointingHandCursor)

    def _on_select(self, combo, label, title, index):
        value = combo.itemText(index)
        label.setText(value)
        # Reset left button text
        combo.clear()
        combo.addItem(title)


    def _bind_combo(self, combo, items_func):
       
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



        # ---------- Receiver type  ----------
        def _ask_receiver_type():
                text, ok = QInputDialog.getText(
                    self.ui.Receiver_type,
                    "Receiver Type",
                    "Enter receiver type:"
                )
                if ok and text:
                    self.ui.Receiver_type.insertItem(0, text)
                    self.ui.Receiver_type.setCurrentIndex(0)

        self.ui.Receiver_type.showPopup = _ask_receiver_type


        # ---------- Antenna Type   ----------
        def _ask_antenna_type():
            text, ok = QInputDialog.getText(
                self.ui.Antenna_type,
                "Antenna Type",
                "Enter antenna type:"
            )
            if ok and text:
                self.ui.Antenna_type.insertItem(0, text)
                self.ui.Antenna_type.setCurrentIndex(0)
        self.ui.Antenna_type.showPopup = _ask_antenna_type       


    # ---------- Mode  ----------
    def _bind_multiselect_combo(self, combo: QComboBox, items_func, label, placeholder: str):
        combo._old_showPopup = combo.showPopup

        def show_popup():
            model = QStandardItemModel(combo)
            for txt in items_func():
                it = QStandardItem(txt)
                it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
                it.setData(Qt.Unchecked, Qt.CheckStateRole)
                model.appendRow(it)
            # Updates the display when the status of items in the model changes
            model.itemChanged.connect(on_item_changed)
            combo.setModel(model)
            combo._old_showPopup()

        def on_item_changed(item: QStandardItem):
            # Spell out all ticked boxes as ‘A, B, C.’
            selected = [
                combo.model().item(r, 0).text()
                for r in range(combo.model().rowCount())
                if combo.model().item(r, 0).checkState() == Qt.Checked
            ]
            label.setText(", ".join(selected) if selected else placeholder)
            

        combo.showPopup = show_popup
        combo.clear()
        combo.addItem(placeholder)
        label.setText(placeholder)

    # ---------- Antenna offset  ----------
    def _open_antenna_offset_dialog(self):
        dlg = QDialog(self.ui.antennaOffsetButton)
        dlg.setWindowTitle("Antenna Offset")

        form = QFormLayout(dlg)
        parts = self.ui.antennaOffsetValue.text().split(",")
        try:
            u0, n0, e0 = [float(x.strip()) for x in parts]
        except:
            u0 = n0 = e0 = 0.0

        sb_u = QDoubleSpinBox(dlg)
        sb_u.setRange(-9999, 9999); sb_u.setDecimals(1); sb_u.setValue(u0)
        sb_n = QDoubleSpinBox(dlg)
        sb_n.setRange(-9999, 9999); sb_n.setDecimals(1); sb_n.setValue(n0)
        sb_e = QDoubleSpinBox(dlg)
        sb_e.setRange(-9999, 9999); sb_e.setDecimals(1); sb_e.setValue(e0)

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

    def _set_antenna_offset(self, sb_u, sb_n, sb_e, dlg):
        u = sb_u.value()
        n = sb_n.value()
        e = sb_e.value()
        self.ui.antennaOffsetValue.setText(f"{u}, {n}, {e}")
        dlg.accept()


    # ---------- Time window - Start & End Date & Time  ----------
    def _open_time_window_dialog(self, _):
        dlg = QDialog(self.ui.timeWindowButton)
        dlg.setWindowTitle("Select start / end time")

        vbox = QVBoxLayout(dlg)
        start_edit = QDateTimeEdit(QDateTime.currentDateTime(), dlg)
        end_edit   = QDateTimeEdit(QDateTime.currentDateTime(), dlg)
        start_edit.setCalendarPopup(True)
        end_edit.setCalendarPopup(True)
        start_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        end_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")

        vbox.addWidget(start_edit)
        vbox.addWidget(end_edit)

        # button
        btn_row = QHBoxLayout()
        ok_btn  = QPushButton("OK", dlg)
        cancel_btn = QPushButton("Cancel", dlg)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        vbox.addLayout(btn_row)

        ok_btn.clicked.connect(lambda: self._set_time_window(start_edit, end_edit, dlg))
        cancel_btn.clicked.connect(dlg.reject)

        dlg.exec()

    def _set_time_window(self, start_edit, end_edit, dlg):
        # If end < start, warn and do not accept dialog
        if end_edit.dateTime() < start_edit.dateTime():
            QMessageBox.warning(
                dlg,  
                "Time error",
                "End time cannot be earlier than start time.\n"
                "Please select again."
            )
            return

        s = start_edit.dateTime().toString("yyyy-MM-dd_HH:mm:ss")
        e = end_edit.dateTime().toString("yyyy-MM-dd_HH:mm:ss")
        self.ui.timeWindowButton.setText(f"{s}\n{e}")
        dlg.accept()
    
    # ---------- Data interval  ---------  
    def _open_data_interval_dialog(self, _):
        # value = 1, minimum = 1, maximum = 3600
        val, ok = QInputDialog.getInt(
            self.ui.dataIntervalButton,          
            "Data interval",                    # title
            "Input interval (seconds):",        # label
            1,                                  # value
            1,                                  # minimum
            999999                                # maximum
        )
        if ok:
            self.ui.dataIntervalButton.setText(f"{val} s")    

    # ----------  generate modified config YAML file (placeholder for backend)  ----------
    def _generate_modified_config_yaml(self, config_parameters):
        """
        Args:
            config_parameters (dict): modified config parameters directory
                example: {
                    'setting1': 'value1',
                    'setting2': 'value2',
                    'nested_config': {
                        'subsetting1': 'subvalue1'
                    }
                }
        
        Returns:
            str: generated YAML file path, should return the path in the format of /resources/Yaml/xxxx.yaml
        
        TODO: backend please implement the following functions:
        1. receive config_parameters parameter
        2. convert the parameters to YAML format
        3. save to /resources/Yaml/ directory
        4. file name format can be: timestamp.yaml, config_v1.yaml, etc.
        5. return the complete file path
        
        Note: the current UI version uses the hardcode path /resources/Yaml/default_config.yaml
        """
        # TODO: backend please implement functions here.
        return self.default_config_path

    # ---------- Show config  ---------
    def on_show_config(self):
        """
        Show config file
        Open the fixed path YAML config file: /resources/Yaml/default_config.yaml
        No longer need to manually select files
        """
        print("opening default config file...")

        # file_path, _ = QFileDialog.getOpenFileName(
        #     None,
        #     "Select a YAML config file",
        #     "",
        #     "YAML files (*.yml *.yaml)"
        # )

        file_path = self.default_config_path
        
        if not os.path.exists(file_path):
            QMessageBox.warning(
                None,
                "File not found",
                f"The file {file_path} does not exist."
            )
            return
        
        if not (file_path.endswith(".yml") or file_path.endswith(".yaml")):
            QMessageBox.warning(
                None,
                "File Format Error",
                f"The file is not a valid YAML file:\n{file_path}"
            )
            return

        self.config_path = file_path

        self.on_open_config_in_editor(self.config_path)


    # ----------  open config file in editor  ----------
    def on_open_config_in_editor(self, file_path):
        """
        Open the config file in an external editor
        
        Args:
            file_path (str): the complete path of the YAML config file
        """
        import os
        import subprocess
        import platform

        if not file_path:
            QMessageBox.warning(
                None,
                "No File Path",
                "No config file path specified."
            )
            return
        
        if not os.path.exists(file_path):
            QMessageBox.critical(
                None,
                "File Not Found",
                f"Config file not found:\n{file_path}"
            )
            return
        
        try:
            abs_path = os.path.abspath(file_path)
            print(f"Opening config file: {abs_path}")
            
            # Open the file with the appropriate method for the operating system
            if platform.system() == "Windows":
                os.startfile(abs_path)
                print("Opened with default Windows application")
                
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", abs_path])
                print("Opened with default macOS application")
                
            else:  # Linux and other Unix-like systems
                subprocess.run(["xdg-open", abs_path])
                print("Opened with default Linux application")
                
        except Exception as e:
            error_message = f"Cannot open config file:\n{file_path}\n\nError: {str(e)}"
            print(f"Error: {error_message}")
            QMessageBox.critical(
                None,
                "Error Opening File",
                error_message
            )

        
    def on_run_pea(self):
        raw = self.ui.timeWindowValue.text()
        print(raw)
        try:
            start_str, end_str = raw.split("to")
            start = datetime.strptime(start_str.strip(), "%Y-%m-%d_%H:%M:%S")
            end   = datetime.strptime(end_str.strip(),   "%Y-%m-%d_%H:%M:%S")
        except ValueError:
            QMessageBox.warning(
                None,
                "Format error",
                "Time window must be in the format:\n"
                "YYYY-MM-DD_HH:MM:SS to YYYY-MM-DD_HH:MM:SS"
            )
            return

        if start > end:
            QMessageBox.warning(
                None,
                "Time error",
                "Start time cannot be later than end time."
            )
            return

        if not getattr(self, "config_path", None):
            QMessageBox.warning(
                None,
                "No config file",
                "Please click Show config and select a YAML file first."
            )
            return

        self.ui.terminalTextEdit.clear()
        self.ui.terminalTextEdit.append("Basic validation passed, starting PEA execution...")
     
        
    def _get_mode_items(self):
        return ["Static","Kinematic","Dynamic"]

    def _get_constellations_items(self):
        return ["GPS", "GAL", "GLO", "BDS", "QZS"]

    def _get_time_window_items(self):
        # Example, can actually be generated dynamically
        return ["2025-04-22 00:00:00", "2025-04-23 00:00:00"]

    def _get_data_interval_items(self):
        return ["1 s", "30 s", "60 s"]

    def _get_receiver_type_items(self):
        return ["Type A", "Type B", "Type C"]

    def _get_antenna_type_items(self):
        return ["Type X", "Type Y", "Type Z"]

    
    def _get_ppp_provider_items(self):
        return ["COD", "GFZ", "JPL", "ESA", "IGS", "WUH"]

    def _get_ppp_series_items(self):
        return ["RAP", "ULT", "FIN"]

    def _get_show_config_items(self):
        return ["Show in Editor", "Show in Dialog"]
