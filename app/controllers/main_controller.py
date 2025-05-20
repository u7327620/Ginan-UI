from pathlib import Path
import shutil
from app.controllers.config_controller import ConfigController
from app.controllers.input_extract_controller import InputExtractController
from app.models.execution import Execution
from app.models.file_integrity import get_pea_exec


class MainController:
    """
    Called when the "Process" button is clicked.

    It is used to run the monolith back-end process to extract the
    user's input in the UI using InputExtractController, and then call PEA
    """
    def __init__(self, ui, input_data_path: str, input_products_path: str, rnx_path: str, output_path: str):
        self.ui = ui
        self.input_data_path = input_data_path
        self.input_products_path = input_products_path
        self.extractor = InputExtractController(self.ui, rnx_path, output_path)

    def execute_backend_process(self):
        """
        The main back-end process that will run the monolith process through PEA
        and return back
        :return:
        """
        extractor = self.extractor

        # 1. Modify the .yaml config file to include the user’s input
        # Create the new .yaml config file
        template_path = "app/resources/Yaml/default_config.yaml"
        config_path = f"app/resources/ppp_{extractor.marker_name}.yaml"
        shutil.copy(template_path, config_path)
        print(f"Template copied to {config_path}")

        # Create the Execution class to write the new config and call PEA
        execution = Execution(config_path, get_pea_exec())

        # Modify the file to include the correct input and output roots
        execution.edit_config("inputs.inputs_root", self.input_data_path, False)
        execution.edit_config("inputs.gnss_observations.gnss_observations_root", self.input_products_path, False)
        execution.edit_config("inputs.gnss_observations.rnx_inputs", extractor.rnx_path, False)
        execution.edit_config("outputs.outputs_root", extractor.output_path, False)

        # Modify the config file to use the right receiver acronym
        execution.config["receiver_options"][extractor.marker_name] = execution.config["receiver_options"].pop("TEST")

        # Modify the file to include the UI extraction values
        execution.edit_config("processing_options.epoch_control.start_epoch", extractor.start_epoch, False)
        execution.edit_config("processing_options.epoch_control.end_epoch", extractor.end_epoch, False)
        execution.edit_config("processing_options.epoch_control.epoch_interval", extractor.epoch_interval, False)
        execution.edit_config(f"receiver_options.{extractor.marker_name}.receiver_type", extractor.receiver_type, False)
        execution.edit_config(f"receiver_options.{extractor.marker_name}.antenna_type", extractor.antenna_type, False)
        execution.edit_config(f"receiver_options.{extractor.marker_name}.models.eccentricity.offset", extractor.antenna_offset, False)

        # Modify the file to include the PPP auto download product values
        #

        # 2. Run PEA using PEAModel.py in the back-end and provide the YAML config file using --config [FILENAME]
        execution.write_config()
        #execution.execute_config()  # Will execute PEA with the provided config

        # 3. PEA processes the data, and eventually outputs the files.
        # Done automatically

        # 4. Plot the output using plot_pos.py or other means.
        # TODO