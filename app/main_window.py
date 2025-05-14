import os
from app.controllers.config_controller import ConfigController
from app.views.main_window_ui import Ui_MainWindow
from PySide6.QtCore import Qt, QRect, QUrl
from PySide6.QtWidgets import QMainWindow, QDialog, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView

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
        # gather controllers for reference, if needed elsewhere
        self.controllers = [self.configCtrl, self.observationCtrl]
        # connect controller ready signal to handler
        self.observationCtrl.ready.connect(self.on_files_ready)

        # —— State variables —— #
        self.rnx_file = None
        self.output_dir = None
        self.current_html = None

        # —— Initial button states —— #
        self.ui.outputButton.setEnabled(False)
        self.ui.processButton.setEnabled(False)

        # —— Signal connections —— #
        # Process button performs processing once both files are selected (enabled by SideBarController)
        self.ui.processButton.clicked.connect(self.process_and_display_fig1)

        # —— Double-click visualization area for full view —— #
        self.ui.visualisationTextEdit.setAttribute(Qt.WA_AcceptTouchEvents)
        # self.ui.visualisationTextEdit.mouseDoubleClickEvent = self.on_double_click_visualisation

    def on_files_ready(self, rnx_path, out_path):
        """Receive selected file paths from SideBarController."""
        self.rnx_file = rnx_path
        self.output_dir = out_path

    def process_and_display_fig1(self):
        if not self.rnx_file:
            self.ui.terminalTextEdit.append("Please select a RNX file first.")
            return
        if not self.output_dir:
            self.ui.terminalTextEdit.append("Please select an output directory first.")
            return

        # Always load example/visual/fig1.html
        fig1 = os.path.join(EXAMPLE_DIR, "visual", "fig1.html")
        self.ui.terminalTextEdit.append(f"Loading fig1.html from: {fig1}")
        if not os.path.exists(fig1):
            self.ui.terminalTextEdit.append(f"Cannot find fig1.html at: {fig1}")
            return

        self.current_html = fig1
        self.display_html(fig1)

    def display_html(self, file_path):
        """
        Embed HTML file into visualisationTextEdit area using QWebEngineView.
        """
        container = self.ui.visualisationTextEdit

        # Clear existing WebEngineView
        for child in container.findChildren(QWebEngineView):
            child.setParent(None)
            child.deleteLater()

        # Create and configure new QWebEngineView
        webview = QWebEngineView(container)
        webview.setUrl(QUrl.fromLocalFile(file_path))

        # Make it fill the entire QTextEdit area
        rect: QRect = container.rect()
        webview.setGeometry(rect)
        webview.show()
        webview.setZoomFactor(0.8)

        # Keep reference to prevent garbage collection
        self.webview = webview

    # def on_double_click_visualisation(self, event):
    #     if not self.current_html:
    #         return
    #     dlg = FullHtmlDialog(self.current_html)
    #     dlg.exec()