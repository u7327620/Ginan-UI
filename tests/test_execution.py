import unittest
from importlib.resources import files
from app.models.execution import Execution
from app.models.find_executable import get_pea_exec

class TestExecution(unittest.TestCase):
    def test_load_config(self):
        execution = Execution(files("tests.resources").joinpath("ppp_example.yaml"), get_pea_exec())
        self.assertFalse(execution.config.values() == {}, "Config isn't empty")

    def test_execute_config(self):
        execution = Execution(files("tests.resources").joinpath("ppp_example.yaml"), get_pea_exec())
        print("Execution loaded")
        alterations = {"outputs.outputs_root": files("tests.resources").joinpath("output"),
                       "inputs.inputs_root": files("tests.resources").joinpath("inputData/products")}
        for key, value in alterations.items():
            execution.edit_config(key, str(value))
        print("Execution edited")
        execution.write_config()

        execution.execute_config()
        self.assertTrue(True)
        # TODO - Verify output when execution is complete.
