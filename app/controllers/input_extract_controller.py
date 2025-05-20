class InputExtractController:
    def __init__(self, ui):
        self.ui = ui

        # Extract user input from the UI and assign it to class variables.
        self.mode = self.ui.Mode.currentText()
        self.constellation = self.ui.Constellations_2.currentText()

        self.time_window = self.ui.timeWindowValue.text()
        self.epoch_interval_raw = self.ui.dataIntervalValue.text()

        self.receiver_type = self.ui.Receiver_type.currentText()
        self.antenna_type = self.ui.Antenna_type.currentText()
        self.antenna_offset_raw = self.ui.antennaOffsetValue.text()

        self.PPP_provider = self.ui.PPP_provider.currentText()
        self.PPP_series = self.ui.PPP_series.currentText()

        # Print verification
        print("🎯 InputExtractController extraction completed：")
        print("mode =", self.mode)
        print("constellation =", self.constellation)
        print("time_window =", self.time_window)
        print("epoch_interval_raw =", self.epoch_interval_raw)
        print("receiver_type =", self.receiver_type)
        print("antenna_type =", self.antenna_type)
        print("antenna_offset_raw =", self.antenna_offset_raw)
        print("PPP_provider =", self.PPP_provider)
        print("PPP_series =", self.PPP_series)
