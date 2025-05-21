import os

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QMainWindow, QDialog, QVBoxLayout,
    QPushButton, QComboBox
)
from PySide6.QtWebEngineWidgets import QWebEngineView

from app.controllers.file_dialog import EXAMPLE_DIR
from app.utils.ui_compilation import compile_ui
from app.controllers.config_controller import ConfigController
from app.controllers.input_extract_controller import InputExtractController
from app.controllers.visualisation_controller import VisualisationController


def setup_main_window():
    try:
        from app.views.main_window_ui import Ui_MainWindow
    except ModuleNotFoundError:
        compile_ui()
        from app.views.main_window_ui import Ui_MainWindow
    return Ui_MainWindow()


class FullHtmlDialog(QDialog):
    def __init__(self, file_path: str):
        super().__init__()
        self.setWindowTitle("Full HTML View")
        layout = QVBoxLayout(self)
        webview = QWebEngineView(self)
        webview.setUrl(QUrl.fromLocalFile(file_path))
        layout.addWidget(webview)
        self.resize(800, 600)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # —— UI Initialization —— #
        self.ui = setup_main_window()
        self.ui.setupUi(self)

        # —— Controllers —— #
        self.configCtrl = ConfigController(self.ui)
        from app.controllers.side_bar_controller import SideBarController
        self.observationCtrl = SideBarController(self.ui, self)
        self.visCtrl = VisualisationController(self.ui, self)
        # If using a live server (e.g. VSCode Live Server):
        self.visCtrl.set_external_base_url("http://127.0.0.1:5501/")
        self.controllers = [self.configCtrl, self.observationCtrl, self.visCtrl]
        self.observationCtrl.ready.connect(self.on_files_ready)

        # —— State variables —— #
        self.rnx_file = None
        self.output_dir = None

        # —— Initial button states —— #
        self.ui.outputButton.setEnabled(False)
        self.ui.processButton.setEnabled(False)

        # —— Signal connections —— #
        self.ui.processButton.clicked.connect(self._on_process_clicked)

        # —— “Open in Browser” button —— #
        self.openInBrowserBtn = QPushButton("Open in Browser", self)
        self.ui.rightLayout.addWidget(self.openInBrowserBtn)
        self.visCtrl.bind_open_button(self.openInBrowserBtn)

        # —— Visual selection drop-down box —— #
        self.visSelector = QComboBox(self)
        self.ui.rightLayout.addWidget(self.visSelector)
        self.visCtrl.bind_selector(self.visSelector)

    def on_files_ready(self, rnx_path: str, out_path: str):
        """Store file paths received from SideBarController."""
        self.rnx_file = rnx_path
        self.output_dir = out_path

    # ------------------------------------------------------------------
    # Processing / visualisation pipeline (minimal version)
    # ------------------------------------------------------------------
    def _on_process_clicked(self):
        """Placeholder for calling backend model; loads fig1 and fig2 for demo."""
        extractor = InputExtractController(self.ui)

        if not self.rnx_file:
            self.ui.terminalTextEdit.append("Please select a RNX file first.")
            return
        if not self.output_dir:
            self.ui.terminalTextEdit.append("Please select an output directory first.")
            return

        # Demo: load both fig1.html and fig2.html
        fig1 = os.path.join(EXAMPLE_DIR, "visual", "fig1.html")
        fig2 = os.path.join(EXAMPLE_DIR, "visual", "fig2.html")

        htmls = []
        for path in (fig1, fig2):
            if os.path.exists(path):
                htmls.append(path)
            else:
                self.ui.terminalTextEdit.append(f"Cannot find file: {path}")

        if not htmls:
            return

        self.ui.terminalTextEdit.append(f"Displaying visualisations: {htmls}")
        self.visCtrl.set_html_files(htmls)

        # ── Replace with real backend call when ready:
        # html_paths = backend.process(self.rnx_file, self.output_dir, **extractor.get_params())
        # self.visCtrl.set_html_files(html_paths)
