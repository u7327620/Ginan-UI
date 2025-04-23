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
