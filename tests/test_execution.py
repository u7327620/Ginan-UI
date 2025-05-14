import unittest
from importlib.resources import files
from app.models.execution import Execution
from app.models.file_integrity import get_pea_exec

class TestExecution(unittest.TestCase):
    def test_load_config(self):
        execution = Execution(files("tests.resources").joinpath("ppp_example.yaml"), get_pea_exec())
        self.assertFalse(execution.config.values() == {}, "Config isn't empty")