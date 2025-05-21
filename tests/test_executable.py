import unittest
from app.models.find_executable import get_pea_exec
from importlib.resources import files
import subprocess

class GetExecutable(unittest.TestCase):
    def test_executable_exists(self):
        self.assertTrue(files('app.resources').joinpath('ginan.AppImage').is_file(), "Executable file should exist")

    def test_finds_executable(self):
        self.assertTrue(get_pea_exec(), "Executable should be found")

    def test_executable(self):
        result = subprocess.call(get_pea_exec(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.assertEqual(result, 0, "Executable should run without error")
