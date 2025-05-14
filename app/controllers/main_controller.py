import shutil

from app.controllers.config_controller import ConfigController
from app.models.execution import Execution
from app.models.file_integrity import get_pea_exec


class MainController:

    def execute_backend_process(self, marker_name: str):
        """
        The main back-end process that will run the monolith process through PEA
        and return back
        :return:
        """
        # 1. Extract the user input from the View and pass it into the Model
        input_data_path = ""
        input_products_path = ""
        output_path = ""
        rnx_path = ""

        mode = "Static"
        start_epoch = "2019-07-18 00:00:00"
        end_epoch = "2019-07-18 23:59:30"
        epoch_interval = "30"
        receiver_type = "LEICA GR25"
        antenna_type = "LEIAR25.R3      NONE"
        antenna_offset_u = "0.0"
        antenna_offset_n = "0.0"
        antenna_offset_e = "0.0"
        antenna_offset = f"[{antenna_offset_u}, {antenna_offset_n}, {antenna_offset_e}]"
        ppp_provider = "ODE"
        ppp_series = "RAP"


        # 2. Modify the .yaml config file to include the user’s input
        # Create the new .yaml config file
        template_path = "resources/ppp_template.yaml"
        config_path = f"resources/ppp_{marker_name}.yaml"

        # Copy the file
        shutil.copy(template_path, config_path)
        print(f"Template copied to {config_path}")

        # Create the Execution class to write the new config and call PEA
        exec = Execution(config_path, get_pea_exec())
            # Already called in __init__: exec.load_config(config_path)

        # Modify the file to include the correct input and output roots
        exec.edit_config("inputs.inputs_root", input_products_path, False)
        exec.edit_config("inputs.gnss_observations.gnss_observations_root", input_data_path, False)
        exec.edit_config("outputs.outputs_root", output_path, False)
        exec.edit_config("inputs.gnss_observations.rnx_inputs", rnx_path, False)

        # Modify the config file to use the right receiver acronym
        exec.config["receiver_options"][marker_name] = exec.config["receiver_options"].pop("TEST")

        # Modify the file to include the UI extraction values
        exec.edit_config("processing_options.epoch_control.start_epoch", start_epoch, False)
        exec.edit_config("processing_options.epoch_control.end_epoch", end_epoch, False)
        exec.edit_config("processing_options.epoch_control.epoch_interval", epoch_interval, False)
        exec.edit_config(f"receiver_options.{marker_name}.receiver_type", receiver_type, False)
        exec.edit_config(f"receiver_options.{marker_name}.antenna_type", antenna_type, False)
        exec.edit_config(f"receiver_options.{marker_name}.models.eccentricity.offset", antenna_offset, False)

        # Modify the file to include the PPP auto download product values
        #

        # 3. Run PEA using PEAModel.py in the back-end and provide the YAML config file using --config [FILENAME]
        exec.write_config()
        exec.execute_config()  # Will execute PEA with the provided config

        # 4. PEA processes the data, and eventually outputs the files.
        # Done automatically

        # 5. Plot the output using plot_pos.py or other means.
