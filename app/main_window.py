import os
from app.controllers.config_controller import ConfigController
from app.views.main_window_ui import Ui_MainWindow
from PySide6.QtCore import Qt, QRect, QUrl
from PySide6.QtWidgets import QMainWindow, QDialog, QVBoxLayout, QPushButton
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QDesktopServices
from app.controllers.input_extract_controller import InputExtractController

# Use the script's directory as base to locate the example/ directory
HERE = os.path.dirname(os.path.abspath(__file__))
EXAMPLE_DIR = os.path.join(HERE, "example")

# set the code good minimal unit test
class FullHtmlDialog(QDialog):
    def __init__(self, file_path):
        super().__init__()
        self.setWindowTitle("Full HTML View")
        layout = QVBoxLayout(self)
        webview = QWebEngineView(self)
        webview.setUrl(QUrl.fromLocalFile(file_path))
        layout.addWidget(webview)
        self.resize(800, 600)

# Visualisation controller embeds HTML into the panel and handles double-click etc.
from app.controllers.visualisation_controller import VisualisationController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # —— UI Initialization —— #
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # —— Controllers —— #
        self.configCtrl = ConfigController(self.ui)
        # SideBarController handles RNX and Output file selection
        from app.controllers.side_bar_controller import SideBarController  # local import avoids circular issues
        self.observationCtrl = SideBarController(self.ui, self)
        self.visCtrl = VisualisationController(self.ui, self)
        # If using a live server (e.g. VSCode Live Server) expose base URL here
        self.visCtrl.set_external_base_url("http://127.0.0.1:5501/")
        # gather controllers for reference, if needed elsewhere
        self.controllers = [self.configCtrl, self.observationCtrl, self.visCtrl]
        # connect controller ready signal to handler
        self.observationCtrl.ready.connect(self.on_files_ready)

        # —— State variables —— #
        self.rnx_file = None
        self.output_dir = None

        # —— Initial button states —— #
        self.ui.outputButton.setEnabled(False)
        self.ui.processButton.setEnabled(False)

        # —— Signal connections —— #
        # Process button performs processing once both files are selected (enabled by SideBarController)
        self.ui.processButton.clicked.connect(self._on_process_clicked)

        # # —— Double-click visualization area for full view —— #
        # self.ui.visualisationTextEdit.setAttribute(Qt.WA_AcceptTouchEvents)

        # create a button to open the current html file in browser
        self.openInBrowserBtn = QPushButton("Open in Browser", self)
        self.openInBrowserBtn.clicked.connect(self._open_current_in_browser)
        self.ui.rightLayout.addWidget(self.openInBrowserBtn)

    def on_files_ready(self, rnx_path, out_path):
        """Store file paths received from SideBarController."""
        self.rnx_file = rnx_path
        self.output_dir = out_path

    # ------------------------------------------------------------------
    # Processing / visualisation pipeline (minimal version)
    # ------------------------------------------------------------------
    def _on_process_clicked(self):
        """Placeholder for calling backend model; minimal version loads example html."""
        # Create a parameter extraction controller to retrieve configuration inputs from the UI.
        extractor = InputExtractController(self.ui)
        
        if not self.rnx_file:
            self.ui.terminalTextEdit.append("Please select a RNX file first.")
            return
        if not self.output_dir:
            self.ui.terminalTextEdit.append("Please select an output directory first.")
            return

        # ── Minimal version: manually use example/visual/fig1.html ── #
        fig1 = os.path.join(EXAMPLE_DIR, "visual", "fig1.html")
        if not os.path.exists(fig1):
            self.ui.terminalTextEdit.append(f"Cannot find fig1.html at: {fig1}")
            return

        self.ui.terminalTextEdit.append(f"Displaying visualisation: {fig1}")
        # Register & show via visualisation controller
        self.visCtrl.set_html_files([fig1])

        # ── Backend processing ── #
        # html_paths = backend.process(rnx_file, output_dir, ...)
        # self.visCtrl.set_html_files(html_paths)

        # open the browser after the html files are set
        import threading
        threading.Timer(1.0, self.visCtrl.open_current_external).start()

    def _open_current_in_browser(self):
        """open the current html file in browser"""
        self.visCtrl.open_current_external() 