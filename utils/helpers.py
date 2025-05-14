import os, shutil
from pathlib import Path


def compile_ui():
    try:
        from app.views.main_window_ui import Ui_MainWindow
    except ImportError:
        ui_file = Path(__file__).parent.parent / "views" / "main_window.ui"
        if shutil.which("pyside6-uic"):
            os.system(f"pyside6-uic {ui_file} -o {ui_file.with_suffix('.py')}")
        else:
            raise ImportError("pyside6-uic is not installed. Please install it to compile the UI.")