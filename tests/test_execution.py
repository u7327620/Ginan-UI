import os
import shutil
import subprocess
import unittest
from importlib.resources import files
from app.models.execution import Execution
from app.utils.find_executable import get_pea_exec

class TestExecution(unittest.TestCase):
    def test_load_sample_config(self):
        execution = Execution(executable=get_pea_exec(), config_path=str(files("tests.resources").joinpath("ppp_example.yaml")))
        self.assertFalse(execution.config.values() == {}, "Caches ppp_example config from tests/resources/ppp_example.yaml")

    def test_copies_template_config(self):
        test_config_path = str(files("tests.resources").joinpath("non_existent.yaml"))
        if os.path.isfile(test_config_path):
            os.remove(test_config_path)
        self.assertFalse(os.path.isfile(test_config_path), "tests/resources/non_existent.yaml shouldn't exist prior to test")
        Execution(executable=get_pea_exec(), config_path=str(files("tests.resources").joinpath("non_existent.yaml")))
        self.assertTrue(os.path.isfile(test_config_path), "tests/resources/non_existent.yaml should be created by execution")


    def test_execute_ppp_example_config(self):
        # common paths
        from tests.resources.common_paths import TEST_DATA_FOLDER, TEST_PRODUCT_FOLDER, TEST_SAMPLE_CONFIG, TEST_OUTPUT_FOLDER

        # Ensure data downloaded
        if not len(os.listdir(TEST_DATA_FOLDER)) > 3:
            subprocess.call("./getData.sh", shell=True, text=True, cwd=TEST_DATA_FOLDER)

        if not len(os.listdir(TEST_PRODUCT_FOLDER)) > 3:
            subprocess.call("./getProducts.sh", shell=True, text=True, cwd=TEST_PRODUCT_FOLDER)

        execution = Execution(get_pea_exec(), TEST_SAMPLE_CONFIG)

        # Clears output folder
        for filename in os.listdir(TEST_OUTPUT_FOLDER):
            file_path = os.path.join(TEST_OUTPUT_FOLDER, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

        # Apply test settings
        alterations = {"outputs.outputs_root": TEST_OUTPUT_FOLDER + "/",
                       "inputs.inputs_root": TEST_PRODUCT_FOLDER + "/"}
        for key, value in alterations.items():
            execution.edit_config(key, value)

        # Executes
        execution.execute_config()

        # Only checks if output is created successfully, not accuracy of output
        self.assertTrue(os.listdir(TEST_OUTPUT_FOLDER), "Output folder should not be empty")
