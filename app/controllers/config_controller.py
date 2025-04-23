# app/controllers/config_controller.py

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

from PySide6.QtCore import Qt, QDate, QDateTime
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QCalendarWidget,
    QDateTimeEdit,
    QInputDialog,
)
from app.views.main_window_ui import Ui_MainWindow

class ConfigController:
    def __init__(self, ui: Ui_MainWindow):
        self.ui = ui

        # bond up QComboBox's showPopup
        self._bind_combo(self.ui.Mode, self._get_mode_items)
        self._bind_combo(self.ui.Constellations_2, self._get_constellations_items)
        # self._bind_combo(self.ui.Time_window, self._get_time_window_items)
        # self._bind_combo(self.ui.Data_interval, self._get_data_interval_items)
        self._bind_combo(self.ui.Receiver_type, self._get_receiver_type_items)
        self._bind_combo(self.ui.Antenna_type, self._get_antenna_type_items)
        # self._bind_combo(self.ui.Antenna_offset, self._get_antenna_offset_items)
        # self._init_date_widget(self.ui.Antenna_offset)
        self._bind_combo(self.ui.PPP_provider, self._get_ppp_provider_items)
        self._bind_combo(self.ui.PPP_series, self._get_ppp_series_items)
        self._bind_combo(self.ui.Show_config, self._get_show_config_items)

        # ---------- Make Time window / Data interval left dropdown purely decorative ----------
        hide_arrow_css = (
            "QComboBox::drop-down{"
            "  subcontrol-origin: padding;"
            "  subcontrol-position: top right;"
            "  width:0px;"
            "  height:0px;"          
            "  border:0px;"
            "}"
            "QComboBox::down-arrow{"
            "  width:0px;"          
            "  height:0px;"
            "}" 
        )

        for cb in (self.ui.Time_window, self.ui.Data_interval):
            cb.setEnabled(False)                       
            cb.setStyleSheet(cb.styleSheet() + hide_arrow_css)


        # Antenna offset：QLineEdit on the right, display only; calendar pops up when clicked on
        self.ui.antennaOffsetValue.mousePressEvent = self._open_calendar_dialog
        self.ui.antennaOffsetValue.setCursor(Qt.PointingHandCursor)
        # Initial value: current date
        self.ui.antennaOffsetValue.setText(QDate.currentDate().toString("dd-MM-yyyy"))

        # Time window：Start & End Date & Time
        self.ui.timeWindowValue.mousePressEvent = self._open_time_window_dialog
        self.ui.timeWindowValue.setCursor(Qt.PointingHandCursor)

        # Data interval：set seconds
        self.ui.dataIntervalValue.mousePressEvent = self._open_data_interval_dialog
        self.ui.dataIntervalValue.setCursor(Qt.PointingHandCursor)



    def _bind_combo(self, combo, items_func):
        """
        Monkey-patch combo.showPopup to:
          1) clear & populate via items_func()
          2) center-align text
          3) call original showPopup to expand
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


    # ---------- Antenna offset  ----------
    def _open_calendar_dialog(self, event):
        dlg = QDialog(self.ui.antennaOffsetValue)
        dlg.setWindowTitle("Select date")
        layout = QVBoxLayout(dlg)

        cal = QCalendarWidget(dlg)
        cal.setSelectedDate(QDate.currentDate())
        layout.addWidget(cal)

        # Check to write text and close
        cal.clicked.connect(lambda d: self._set_offset_date(d, dlg))
        dlg.exec()

    def _set_offset_date(self, qdate: QDate, dlg: QDialog):
        self.ui.antennaOffsetValue.setText(qdate.toString("dd-MM-yyyy"))
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
            self.ui.dataIntervalValue.setText(f"{val} s")       


    def _get_mode_items(self):
        return ["Static", "Dynamic"]

    def _get_constellations_items(self):
        return ["GPS", "GAL", "GLO", "BDS"]

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
        return ["Provider A", "Provider B", "Provider C"]

    def _get_ppp_series_items(self):
        return ["Series 1", "Series 2", "Series 3"]

    def _get_show_config_items(self):
        return ["Show in Editor", "Show in Dialog"]
