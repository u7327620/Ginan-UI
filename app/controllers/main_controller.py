import re
from pathlib import Path
import shutil
from dataclasses import dataclass
from importlib.resources import files

from app.models.execution import Execution
from app.models.find_executable import get_pea_exec

#region UI Input Extraction

def determine_mode_value(mode_raw: str) -> int:
    if mode_raw == "Static":
        return 0
    elif mode_raw == "Kinematic":
        return 30
    elif mode_raw == "Dynamic":
        return 100
    else:
        raise ValueError(f"Unknown mode: {mode_raw!r}")


def extract_marker_name(rnx_path: str) -> str:
    """
    Extracts the 4-char site code from the RNX file name.
    Falls back to "TEST" if one cannot be found.
    E.g.: ALIC00AUS_R_20250190000_01D_30S_MO.rnx.gz -> ALBY
    """
    if not rnx_path:
        return "TEST"
    stem = Path(rnx_path).stem  # drops .gz/.rnx
    m = re.match(r"([A-Za-z]{4})", stem)
    return m.group(1).upper() if m else "TEST"

def parse_time_window(time_window_raw: str):
    """Convert 'start_time to end_time' into (start_epoch, end_epoch)."""
    try:
        start, end = map(str.strip, time_window_raw.split("to"))
        return start, end
    except ValueError:
        raise ValueError("Invalid time_window format. Expected: 'start_time to end_time'")

def parse_antenna_offset(antenna_offset_raw: str):
    """Convert 'u, n, e' into [u, n, e] floats."""
    try:
        u, n, e = map(str.strip, antenna_offset_raw.split(","))
        return [float(u), float(n), float(e)]
    except ValueError:
        raise ValueError("Invalid antenna offset format. Expected: 'u, n, e'")

# Simple dataclass that stores the UI input extracted values
@dataclass
class ExtractedInputs:
    # Parsed / derived values
    marker_name: str
    start_epoch: str
    end_epoch: str
    epoch_interval: int
    antenna_offset: list[float]
    mode: int

    # Raw strings / controls that are needed downstream
    constellations_raw: str
    receiver_type: str
    antenna_type: str
    ppp_provider: str
    ppp_series: str

    # File paths associated to this run
    rnx_path: str
    output_path: str

#endregion

class MainController:
    """
    Back-end controller

    Called when the "Process" button is clicked.
    It gathers UI input, writes the YAML config, and calls PEA.
    """

    def __init__(self, ui, input_data_path: str, input_products_path: str, rnx_path: str, output_path: str):
        self.ui = ui
        self.input_data_path = input_data_path
        self.input_products_path = input_products_path
        self.rnx_path = rnx_path
        self.output_path = output_path

    def extract_ui_values(self, rnx_path):
        # Extract user input from the UI and assign it to class variables.
        mode_raw           = self.ui.modeValue.text()
        constellations_raw = self.ui.constellationsValue.text()
        time_window_raw    = self.ui.timeWindowValue.text()
        epoch_interval_raw = self.ui.dataIntervalValue.text()
        receiver_type      = self.ui.receiverTypeValue.text()
        antenna_type       = self.ui.antennaTypeValue.text()
        antenna_offset_raw = self.ui.antennaOffsetValue.text()
        ppp_provider       = self.ui.pppProviderValue.text()
        ppp_series         = self.ui.pppSeriesValue.text()

        # Parsed values
        start_epoch, end_epoch = parse_time_window(time_window_raw)
        antenna_offset         = parse_antenna_offset(antenna_offset_raw)
        epoch_interval         = int(epoch_interval_raw.replace("s", "").strip())
        marker_name            = extract_marker_name(rnx_path)
        mode                   = determine_mode_value(mode_raw)

        # Print verification
        print("InputExtractController Extraction Completed：")
        print("mode =", mode)
        print("constellation =", constellations_raw)
        print("start_epoch =", start_epoch)
        print("end_epoch =", end_epoch)
        print("epoch_interval =", epoch_interval)
        print("receiver_type =", receiver_type)
        print("antenna_type =", antenna_type)
        print("antenna_offset =", antenna_offset)
        print("PPP_provider =", ppp_provider)
        print("PPP_series =", ppp_series)
        print("marker = ", marker_name)

        # Returned the values found as a dataclass for easier access
        return ExtractedInputs(
            marker_name=marker_name,
            start_epoch=start_epoch,
            end_epoch=end_epoch,
            epoch_interval=epoch_interval,
            antenna_offset=antenna_offset,
            mode=mode,
            constellations_raw=constellations_raw,
            receiver_type=receiver_type,
            antenna_type=antenna_type,
            ppp_provider=ppp_provider,
            ppp_series=ppp_series,
            rnx_path=rnx_path,
            output_path=self.output_path,
        )

    def execute_backend_process(self):
        """
        The main back-end process that will run the monolith process through PEA
        and return back
        :return:
        """

        # 0. Pull all UI values into usable variables
        inputs = self.extract_ui_values(self.rnx_path)

        # 1. Copy .yaml template to a run-specific config path
        template_path = str(files("app.resources").joinpath("Yaml/default_config.yaml"))
        config_path = str(files("app.resources").joinpath(f"ppp_{inputs.marker_name}.yaml"))
        shutil.copy(template_path, config_path)
        print(f"Template copied to {config_path}")

        # 2. Create the Execution class to write the new config and call PEA
        execution = Execution(config_path, get_pea_exec())

        # 3. Set core inputs / outputs
        execution.edit_config("inputs.inputs_root", self.input_data_path, False)
        execution.edit_config("inputs.gnss_observations.gnss_observations_root", self.input_products_path, False)
        execution.edit_config("inputs.gnss_observations.rnx_inputs", inputs.rnx_path, False)
        execution.edit_config("outputs.outputs_root", inputs.output_path, False)

        # 4. Modify the config file to use the right receiver acronym
        if "TEST" in execution.config.get("receiver_options", {}):
            execution.config["receiver_options"][inputs.marker_name] = execution.config["receiver_options"].pop("TEST")

        # 5. Modify the file to include the UI extraction values
        execution.edit_config("processing_options.epoch_control.start_epoch", inputs.start_epoch, False)
        execution.edit_config("processing_options.epoch_control.end_epoch", inputs.end_epoch, False)
        execution.edit_config("processing_options.epoch_control.epoch_interval", inputs.epoch_interval, False)
        execution.edit_config(f"receiver_options.{inputs.marker_name}.receiver_type", inputs.receiver_type, False)
        execution.edit_config(f"receiver_options.{inputs.marker_name}.antenna_type", inputs.antenna_type, False)
        execution.edit_config(f"receiver_options.{inputs.marker_name}.models.eccentricity.offset", inputs.antenna_offset, False)
        execution.edit_config("estimation_parameters.receivers.global.pos.process_noise", inputs.mode, False)

        # 6. Enable the constellations
        if inputs.constellations_raw:
            for const in inputs.constellations_raw.split(","):
                const_key = const.strip().lower()
                if const_key:
                    execution.edit_config(f"processing_options.gnss_general.sys_options.{const_key}.process", True, False)

        # 7. Modify the file to include the PPP auto download product values
        # TODO

        # 8. Run PEA using PEAModel.py in the back-end and provide the YAML config file using --config [FILENAME]
        execution.write_config()
        #execution.execute_config()  # Will execute PEA with the provided config

        # 9. Plot the output using plot_pos.py or other means.
        # TODO