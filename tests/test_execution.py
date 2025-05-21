import os
import shutil
import subprocess
import unittest
from importlib.resources import files
from app.models.execution import Execution
from app.models.find_executable import get_pea_exec

class TestExecution(unittest.TestCase):
    def test_load_config(self):
        execution = Execution(files("tests.resources").joinpath("ppp_example.yaml"), get_pea_exec())
        self.assertFalse(execution.config.values() == {}, "Config isn't empty")

    def test_execute_config(self):
        data_folder = files("tests.resources").joinpath("inputData/data")
        product_folder = files("tests.resources").joinpath("inputData/products")
        if not len(os.listdir(str(data_folder))) > 3:
            subprocess.call("./getData.sh", shell=True, text=True, cwd=str(data_folder))

        if not len(os.listdir(str(product_folder))) > 3:
            subprocess.call("./getProducts.sh", shell=True, text=True, cwd=str(product_folder))

        execution = Execution(files("tests.resources").joinpath("ppp_example.yaml"), get_pea_exec())
        folder_path = str(files("tests.resources").joinpath("output"))
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

        alterations = {"outputs.outputs_root": files("tests.resources").joinpath("output"),
                       "inputs.inputs_root": files("tests.resources").joinpath("inputData/products")}
        for key, value in alterations.items():
            execution.edit_config(key, str(value))

        execution.execute_config()
        self.assertTrue(os.listdir(folder_path), "Output folder should not be empty")
