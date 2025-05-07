from app.controllers.file_dialog import FileDialogController
from app.controllers.config_controller import ConfigController  # Ensure this is imported
from app.views.main_window_ui import Ui_MainWindow
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QFileDialog, QMainWindow, QDialog, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt

class FullHtmlDialog(QDialog):
    def __init__(self, file_path):
        super().__init__()
        self.setWindowTitle("Full HTML View")
        self.webview = QWebEngineView(self)
        self.webview.setUrl(QUrl.fromLocalFile(file_path))
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.webview)

        self.setLayout(layout)
        self.resize(800, 600)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.models = []
        self.controllers = []
        self.setup_controllers()

        # Connect buttons
        self.ui.observationsButton.clicked.connect(self.load_html_file)
        self.ui.processButton.clicked.connect(self.process_html_file)

        # Enable double-click event for visualisationTextEdit
        self.ui.visualisationTextEdit.setAttribute(Qt.WA_AcceptTouchEvents)
        self.ui.visualisationTextEdit.mouseDoubleClickEvent = self.on_double_click_visualisation

    def setup_controllers(self):
        # Initialize FileDialogController and ConfigController
        # self.controllers.append(FileDialogController(self.ui, ""))  # No model for now
        self.controllers.append(FileDialogController(self.ui, None))
        self.controllers.append(ConfigController(self.ui))  # Initialize ConfigController

    def load_html_file(self):
        """
        Opens a dialog to select an HTML file from the 'example' folder and loads it.
        """
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select HTML File", "example", "HTML Files (*.html);;All Files (*)", options=options
        )

        if file_path:
            self.display_html(file_path)

    def display_html(self, file_path):
        """
        Loads the selected HTML file into the visualization area using QWebEngineView.
        """
        if hasattr(self.ui, 'visualisationTextEdit'):
            # Create a QWebEngineView to render the HTML
            self.webview = QWebEngineView(self)
            self.webview.setUrl(QUrl.fromLocalFile(file_path))
            self.webview.setGeometry(self.ui.visualisationTextEdit.geometry())
            self.webview.show()

            # Store the file path to use later for full HTML view
            self.set_current_html_file(file_path)

            # Adjust visualization (ensure the content is rendered properly)
            self.scale_visualization()

    def scale_visualization(self):
        """
        Adjust the visual representation to fit the visualisationTextEdit area.
        """
        # Set the zoom factor to ensure the HTML content fits
        self.webview.setZoomFactor(0.8)

    def process_html_file(self):
        """
        Handle the process button click to finalize visualization.
        """
        print("Processing the HTML file and rendering in the visualisation area.")
        # You can add any processing logic here if needed.

    def on_double_click_visualisation(self, event):
        """
        Handle the double-click event on the visualisation area to open the full HTML in a dialog.
        """
        if hasattr(self, 'current_html_file'):
            file_path = self.current_html_file
            # Open the full HTML in a new dialog
            dialog = FullHtmlDialog(file_path)
            dialog.exec()

    def set_current_html_file(self, file_path):
        """
        Store the current file path for later reference when double-clicking to view the full HTML.
        """
        self.current_html_file = file_path
