import os
from importlib.resources import files

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QMainWindow, QDialog, QVBoxLayout, QPushButton, QComboBox
from PySide6.QtWebEngineWidgets import QWebEngineView

from app.utils.ui_compilation import compile_ui
from app.controllers.main_controller import MainController
from app.controllers.input_controller import InputController
from app.controllers.visualisation_controller import VisualisationController

def setup_main_window():
    try :
        # Attempts to import the UI
        from app.views.main_window_ui import Ui_MainWindow
    except ModuleNotFoundError:
        compile_ui()
        from app.views.main_window_ui import Ui_MainWindow
    window = Ui_MainWindow()
    return window

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
    """
    Top-level QMainWindow that is essential for the app to run. It:
        - Builds the UI
        - Composes InputController and VisualisationController
        - Owns the Process action to start PEA
        - Listens for InputController.ready(rnx_path, output_path)
        - Invokes MainController to generate PPP outputs and drive visualisation.
    """

    def __init__(self):
        super().__init__()

        # —— UI Initialization —— #
        self.ui = setup_main_window()
        self.ui.setupUi(self)

        # —— Controllers —— #
        self.inputCtrl = InputController(self.ui, self)
        self.visCtrl = VisualisationController(self.ui, self)

        # Can remove?: external base URL for live server previews
        # self.visCtrl.set_external_base_url("http://127.0.0.1:5501/")

        # Keep a simple list if you need to iterate or manage controllers
        self.controllers = [self.inputCtrl, self.visCtrl]

        # RNX/Output selection readiness
        self.inputCtrl.ready.connect(self.on_files_ready)

        # —— State variables —— #
        self.rnx_file:   str | None = None
        self.output_dir: str | None = None

        # —— Initial button states —— #
        self.ui.outputButton.setEnabled(False)
        self.ui.processButton.setEnabled(False)

        # —— Signal connections —— #
        # MainWindow is the single owner of the "Process" action
        self.ui.processButton.clicked.connect(self._on_process_clicked)

        # —— Visualisation helpers —— #
        self.openInBrowserBtn = QPushButton("Open in Browser", self)
        self.ui.rightLayout.addWidget(self.openInBrowserBtn)
        self.visCtrl.bind_open_button(self.openInBrowserBtn)

        self.visSelector = QComboBox(self)
        self.ui.rightLayout.addWidget(self.visSelector)
        self.visCtrl.bind_selector(self.visSelector)

    def on_files_ready(self, rnx_path: str, out_path: str):
        """Store file paths received from InputController."""
        self.rnx_file = rnx_path
        self.output_dir = out_path

    #region Processing / Visualisation
    def _on_process_clicked(self):
        """Call backend model to generate outputs; then visualise as needed."""

        if not self.rnx_file:
            self.ui.terminalTextEdit.append("Please select a RNX file first.")
            return
        if not self.output_dir:
            self.ui.terminalTextEdit.append("Please select an output directory first.")
            return

        # —— Launch the backend —— #
        try:
            controller = MainController(
                self.ui,
                str(files("tests.resources").joinpath("inputData")),
                str(files("tests.resources").joinpath("inputData/products")),
                self.rnx_file,
                self.output_dir,
            )

            # Call the backend process
            controller.execute_backend_process()
            self.ui.terminalTextEdit.append("✔️ Processing finished.")
        except Exception as err:
            self.ui.terminalTextEdit.append(f"❌ Processing failed: {err}")



        # ── Minimal version: manually use example/visual/fig1.html ── #
        #fig1 = os.path.join(EXAMPLE_DIR, "visual", "fig1.html")
        #if not os.path.exists(fig1):
        #    self.ui.terminalTextEdit.append(f"Cannot find fig1.html at: {fig1}")
        #    return

        #self.ui.terminalTextEdit.append(f"Displaying visualisation: {fig1}")
        # Register & show via visualisation controller
        #self.visCtrl.set_html_files([fig1])

        # ── Replace with real backend call when ready:
        # html_paths = backend.process(self.rnx_file, self.output_dir, **extractor.get_params())
        # self.visCtrl.set_html_files(html_paths)

    #endregion