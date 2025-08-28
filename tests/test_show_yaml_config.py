import unittest

from app.main_window import MainWindow
from app.models.execution import Execution
from app.utils.find_executable import get_pea_exec
from app.utils.yaml import load_yaml
from app.controllers.input_controller import InputController
from tests.resources.common_paths import *
import os

class ShowYamlConfig(unittest.TestCase):
    def test_write_config(self):
        if os.path.isfile(TEST_NON_EXISTENT_CONFIG):
            os.remove(TEST_NON_EXISTENT_CONFIG)
        execution = Execution(executable=get_pea_exec(), config_path=TEST_NON_EXISTENT_CONFIG)
        execution.edit_config("inputs.inputs_root", "/")

        # 1. The changes should remain cached until there's a reason to write
        current_write = load_yaml(TEST_NON_EXISTENT_CONFIG)
        self.assertFalse(current_write["inputs"]["inputs_root"] == "/")

        # 2. The changes should be written when write_cached is called
        execution.write_cached_changes()
        current_write = load_yaml(TEST_NON_EXISTENT_CONFIG)
        self.assertTrue(current_write["inputs"]["inputs_root"] == "/")

        os.remove(TEST_NON_EXISTENT_CONFIG)
