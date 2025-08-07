import os
import glob
from importlib.resources import files

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QMainWindow, QDialog, QVBoxLayout, QPushButton, QComboBox
from PySide6.QtWebEngineWidgets import QWebEngineView

from app.models.execution import Execution, GENERATED_YAML
from app.models.find_executable import get_pea_exec
from app.utils.ui_compilation import compile_ui
from app.controllers.input_controller import InputController
from app.controllers.visualisation_controller import VisualisationController


def setup_main_window():
    # Whilst developing, we compile every time :)
    #try :
    #    from app.views.main_window_ui import Ui_MainWindow
    #except ModuleNotFoundError:
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
        self.execution = Execution(get_pea_exec())
        self.inputCtrl = InputController(self.ui, self, self.execution)
        self.visCtrl = VisualisationController(self.ui, self)

        # Can remove?: external base URL for live server previews
        # self.visCtrl.set_external_base_url("http://127.0.0.1:5501/")

        # Keep a simple list if you need to iterate or manage controllers
        self.controllers = [self.inputCtrl, self.visCtrl]

        # RNX/Output selection readiness
        self.inputCtrl.ready.connect(self.on_files_ready)

        # PEA processing readiness
        self.inputCtrl.pea_ready.connect(self._on_process_clicked)

        # —— State variables —— #
        self.rnx_file:   str | None = None
        self.output_dir: str | None = None

        # —— Signal connections —— #
        # Note: processButton.clicked is now handled by InputController for basic validation
        # MainWindow will handle the actual PEA processing through a different mechanism

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
        
        # just for sprint 4 show 
        html_dir = os.path.join(self.output_dir, "visual")
        pattern = os.path.join(html_dir, "*.html")
        html_files = sorted(glob.glob(pattern))
        if not html_files:
            self.ui.terminalTextEdit.append(f"Cannot find any .html in {html_dir}")
            return
        self.ui.terminalTextEdit.append(f"Displaying {len(html_files)} visualisation(s) from {html_dir}")
        self.visCtrl.set_html_files(html_files)
        



        # # ── Minimal version: manually use example/visual/fig1.html ── #
        # fig1 = os.path.join(EXAMPLE_DIR, "visual", "fig1.html")
        # if not os.path.exists(fig1):
        #    self.ui.terminalTextEdit.append(f"Cannot find fig1.html at: {fig1}")
        #    return

        # self.ui.terminalTextEdit.append(f"Displaying visualisation: {fig1}")
        # # Register & show via visualisation controller
        # self.visCtrl.set_html_files([fig1])

        # # ── Replace with real backend call when ready:
        # html_paths = backend.process(self.rnx_file, self.output_dir, **extractor.get_params())
        # self.visCtrl.set_html_files(html_paths)

    #endregion