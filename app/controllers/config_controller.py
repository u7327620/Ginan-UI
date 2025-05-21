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

        # bond up QComboBox's showPopup
        self._bind_combo(self.ui.Mode, self._get_mode_items)
        self._bind_combo(self.ui.PPP_provider, self._get_ppp_provider_items)
        self._bind_combo(self.ui.PPP_series, self._get_ppp_series_items)

        # Multiple Choice Binding
        self._bind_multiselect_combo(self.ui.Constellations_2,
                                     self._get_constellations_items,
                                     self.ui.constellationsValue,
                                     placeholder="Constellations")


        # When selected, write the value to the right Label and reset the left text.
        # Mode, Constellations...
        self.ui.Mode.activated.connect(
            lambda idx: self._on_select(self.ui.Mode, self.ui.modeValue, "Mode", idx))
        self.ui.antennaOffsetButton.clicked.connect(self._open_antenna_offset_dialog)
        self.ui.antennaOffsetButton.setCursor(Qt.PointingHandCursor)
        self.ui.antennaOffsetValue.setText("0.0, 0.0, 0.0")
        self.ui.Antenna_type.activated.connect(
            lambda idx: self._on_select(self.ui.Antenna_type, self.ui.antennaTypeValue, "Antenna type", idx))
        self.ui.PPP_provider.activated.connect(
            lambda idx: self._on_select(self.ui.PPP_provider, self.ui.pppProviderValue, "PPP provider", idx))
        self.ui.PPP_series.activated.connect(
            lambda idx: self._on_select(self.ui.PPP_series, self.ui.pppSeriesValue, "PPP series", idx))


        
        

        # Time window：Start & End Date & Time
        self.ui.timeWindowButton.clicked.connect(self._open_time_window_dialog)
        self.ui.timeWindowButton.setCursor(Qt.PointingHandCursor)

        # Data interval：set seconds
        self.ui.dataIntervalButton.clicked.connect(self._open_data_interval_dialog)
        self.ui.dataIntervalButton.setCursor(Qt.PointingHandCursor)

        # Show config: Click the button to open the editor
        self.ui.showConfigButton.clicked.connect(self._open_show_config)
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
                    # update left ComboBox 
                    self.ui.Receiver_type.clear()
                    self.ui.Receiver_type.addItem(text)
                    # update right Label
                    self.ui.receiverTypeValue.setText(text)

        self.ui.Receiver_type.showPopup = _ask_receiver_type
        self.ui.receiverTypeValue.setText("")

        # ---------- Antenna Type   ----------
        def _ask_antenna_type():
            text, ok = QInputDialog.getText(
                self.ui.Antenna_type,
                "Antenna Type",
                "Enter antenna type:"
            )
            if ok and text:
                self.ui.Antenna_type.clear()
                self.ui.Antenna_type.addItem(text)
                self.ui.antennaTypeValue.setText(text)
        self.ui.Antenna_type.showPopup = _ask_antenna_type
        self.ui.antennaTypeValue.setText("")

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
        # 从现有文本解析初始值
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
        dlg = QDialog(self.ui.timeWindowValue)
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
        self.ui.timeWindowValue.setText(f"{s}  →  {e}")
        dlg.accept()
    
    # ---------- Data interval  ---------  
    def _open_data_interval_dialog(self, _):
        # value = 1, minimum = 1, maximum = 3600
        val, ok = QInputDialog.getInt(
            self.ui.dataIntervalValue,          # parent
            "Data interval",                    # title
            "Input interval (seconds):",        # label
            1,                                  # value
            1,                                  # minimum
            3600                                # maximum
        )
        if ok:
            self.ui.dataIntervalValue.setText(str(val))      

    # ---------- Show config  ---------
    def _open_show_config(self):
        """
        Temporarily replace the yaml folder with the project root folder
        """
        # __file__ is the path to config_controller.py, two levels up to the project root.
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..')
        )

        if not os.path.isdir(project_root):
            print(f"Project root directory does not exist: {project_root}")
            return

        # Cross-platform opening of directories with the system's default file manager
        url = QUrl.fromLocalFile(project_root)
        QDesktopServices.openUrl(url)




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
