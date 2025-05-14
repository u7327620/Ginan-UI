# app/controllers/file_dialog.py

import os
from PySide6.QtWidgets import QFileDialog

HERE = os.path.dirname(os.path.abspath(__file__))
EXAMPLE_DIR = os.path.normpath(os.path.join(HERE, "..", "example"))
OUTPUT_DIR = os.path.join(EXAMPLE_DIR, "output")

def select_rnx_file(parent) -> str:
    caption = "Select RINEX File"
    filters = "RINEX Files (*.rnx *.rnx.gz);;All Files (*)"
    path, _ = QFileDialog.getOpenFileName(parent, caption, "", filters)
    return path or ""


def select_output_dir(parent) -> str:
    """Open a dialog to choose a directory to save output files."""
    default_dir = OUTPUT_DIR if os.path.isdir(OUTPUT_DIR) else HERE
    caption = "Select Output Directory"
    # Use getExistingDirectory to pick a folder.
    path = QFileDialog.getExistingDirectory(parent, caption, default_dir)
    return path or ""
