import os
import unittest
from app.models.file_integrity import get_pea_exec
import subprocess

class GetExecutable(unittest.TestCase):
    def test_executable_exists(self):
        self.assertTrue(os.path.isfile(f"{os.getcwd()}/../app/resources/ginan.AppImage"))
    def test_finds_executable(self):
        self.assertTrue(get_pea_exec())
    def test_executable(self):
        result = subprocess.call(get_pea_exec(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.assertEqual(result, 0, "Executable should run without error")

if __name__ == '__main__':
    unittest.main()
