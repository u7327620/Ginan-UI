import subprocess, shutil
from pathlib import Path


def compile_ui():
    ui_file = Path(__file__).parent.parent / "app" / "views" / "main_window.ui"
    output_file = Path(__file__).parent.parent / "app" / "views" / "main_window_ui.py"
    if shutil.which("pyside6-uic"):
        with open(output_file, 'w') as f:
            f.write("# This file is auto-generated. Do not edit.\n")
        result = subprocess.run(["pyside6-uic", ui_file, "-o", output_file], capture_output=True)
        if result.returncode != 0:
            print(f"Error compiling UI: {result.stderr.decode()}")
        else:
            print("UI compiled successfully.")
            print(result.stdout.decode())
    else:
        raise ImportError("pyside6-uic is not installed. Please install it to compile the UI.")