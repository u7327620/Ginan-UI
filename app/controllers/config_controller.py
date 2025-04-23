# app/controllers/config_controller.py

from PySide6.QtCore import Qt
from app.views.main_window_ui import Ui_MainWindow

class ConfigController:
    def __init__(self, ui: Ui_MainWindow):
        self.ui = ui

        # bond up QComboBox's showPopup
        self._bind_combo(self.ui.Mode, self._get_mode_items)
        self._bind_combo(self.ui.Constellations_2, self._get_constellations_items)
        self._bind_combo(self.ui.Time_window, self._get_time_window_items)
        self._bind_combo(self.ui.Data_interval, self._get_data_interval_items)
        self._bind_combo(self.ui.Receiver_type, self._get_receiver_type_items)
        self._bind_combo(self.ui.Antenna_type, self._get_antenna_type_items)
        self._bind_combo(self.ui.Antenna_offset, self._get_antenna_offset_items)
        self._bind_combo(self.ui.PPP_provider, self._get_ppp_provider_items)
        self._bind_combo(self.ui.PPP_series, self._get_ppp_series_items)
        self._bind_combo(self.ui.Show_config, self._get_show_config_items)

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

    def _get_antenna_offset_items(self):
        return ["0,0,0", "1,1,1", "2,2,2"]

    def _get_ppp_provider_items(self):
        return ["Provider A", "Provider B", "Provider C"]

    def _get_ppp_series_items(self):
        return ["Series 1", "Series 2", "Series 3"]

    def _get_show_config_items(self):
        return ["Show in Editor", "Show in Dialog"]
