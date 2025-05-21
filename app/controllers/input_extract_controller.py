from pathlib import Path
import re

class InputExtractController:
    def __init__(self, ui, rnx_path: str = "", output_path: str = ""):
        self.ui = ui

        # Extract "Observations" and "Output" paths from UI
        self.rnx_path = rnx_path
        self.output_path = output_path

        # Extract user input from the UI and assign it to class variables.
        self.mode_raw = self.ui.modeValue.text()
        self.constellation = self.ui.constellationsValue.text()
        self.time_window_raw = self.ui.timeWindowValue.text()
        self.epoch_interval_raw = self.ui.dataIntervalValue.text()
        self.receiver_type = self.ui.receiverTypeValue.text()
        self.antenna_type = self.ui.antennaTypeValue.text()
        self.antenna_offset_raw = self.ui.antennaOffsetValue.text()
        self.ppp_provider = self.ui.pppProviderValue.text()
        self.ppp_series = self.ui.pppSeriesValue.text()

        # Parsed values
        self.start_epoch, self.end_epoch = self.parse_time_window()
        self.antenna_offset = self.parse_antenna_offset()
        self.epoch_interval = self.epoch_interval_raw.replace("s", "").strip()
        self.marker_name = self.extract_marker_name()
        self.mode = self.determine_mode_value()

        # Print verification
        print("InputExtractController Extraction Completed：")
        print("mode =", self.mode)
        print("constellation =", self.constellation)
        print("start_epoch =", self.start_epoch)
        print("end_epoch =", self.end_epoch)
        print("epoch_interval =", self.epoch_interval)
        print("receiver_type =", self.receiver_type)
        print("antenna_type =", self.antenna_type)
        print("antenna_offset =", self.antenna_offset)
        print("PPP_provider =", self.ppp_provider)
        print("PPP_series =", self.ppp_series)

    def parse_time_window(self):
        """Convert the raw "start_time to end_time" format of time_window to two usable variables start_epoch and end_epoch"""
        try:
            start, end = map(str.strip, self.time_window_raw.split("to"))
            return start, end
        except ValueError:
            raise ValueError("Invalid time_window format. Expected: 'start_time to end_time'")

    def parse_antenna_offset(self):
        """Convert the raw "0.0, 0.0, 0.0" format of antenna_offset to three usable variables, and return in correct formatting"""
        try:
            test = "0.0, 0.0, 0.0"
            u, n, e = map(str.strip, test.split(",")) #self.antenna_offset_raw.split(","))
            return f"[{u}, {n}, {e}]"
        except ValueError:
            raise ValueError("Invalid antenna offset format. Expected: 'u, n, e'")

    def extract_marker_name(self):
        """
        Extracts the 4-char site code from the RNX file name
        Will fall back to "TEST" if one cannot be found
        E.g.: ALIC00AUS_R_20250190000_01D_30S_MO.rnx.gz  ->  ALBY
        """
        if not self.rnx_path:
            return "TEST"

        stem = Path(self.rnx_path).stem # Drops the .gz / .rnx file path ending
        m = re.match(r"([A-Za-z]{4})", stem)
        return m.group(1).upper() if m else "TEST"

    def determine_mode_value(self):
        if self.mode_raw == "Static":
            return 0
        elif self.mode_raw == "Kinematic":
            return 30
        elif self.mode_raw == "Dynamic":
            return 100