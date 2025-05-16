# app/controllers/visualisation_controller.py
"""Controller responsible for everything inside the visualisation panel.

Responsibilities
----------------
1. Embed one of the generated HTML files into the QTextEdit area.
2. Maintain a list (indexed) of available HTML visualisations.
3. Provide a double-click handler and an explicit *Open* action that open the
   current html in the user's default browser.

NOTE:  UI widgets for selecting visualisation (e.g. a ComboBox or QListWidget)
       and an *Open* button are **not** yet present in the .ui file.  This
       controller exposes stub `bind_open_button()` / `bind_selector()` helpers
       which can be called once those widgets are added.
"""
from __future__ import annotations

import os
from typing import List, Sequence, Optional
from PySide6.QtCore import QRect, QUrl, QObject, QEvent, Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QTextEdit, QPushButton, QComboBox
from PySide6.QtWebEngineWidgets import QWebEngineView

class VisualisationController(QObject):
    """Manage visualisation panel interactions."""

    def __init__(self, ui, parent_window):
        super().__init__(parent_window)
        self.ui = ui  # Ui_MainWindow instance
        self.parent = parent_window
        self.html_files: List[str] = []  # paths of available visualisations
        self.current_index: int | None = None
        # base URL (e.g. http://127.0.0.1:5501/) to convert local paths when opening externally
        self.external_base_url: Optional[str] = None

        # Install event filter on the container to catch double-clicks
        self.ui.visualisationTextEdit.installEventFilter(self)

    # ---------------------------------------------------------------------
    # Public API (to be called from MainWindow / other controllers)
    # ---------------------------------------------------------------------
    def set_html_files(self, paths: Sequence[str]):
        """Register the list of generated html files and default to #0."""
        self.html_files = list(paths)
        if self.html_files:
            self.display_html(0)

    def display_html(self, index: int):
        """Embed the *index*-th html into the QTextEdit panel."""
        if not (0 <= index < len(self.html_files)):
            return  # out of range
        file_path = self.html_files[index]
        self.current_index = index
        self._embed_html(file_path)

    def open_current_external(self):
        """Open the currently displayed html in the system web browser."""
        if self.current_index is None:
            return
        path = self.html_files[self.current_index]
        if self.external_base_url:
            # compute relative path to project root
            import pathlib, os
            try:
                project_root = pathlib.Path(__file__).resolve().parents[2]  # .../app/controllers -> project root
                rel_path = pathlib.Path(path).resolve().relative_to(project_root)
                url = self.external_base_url + str(rel_path).replace(os.sep, '/')
                QDesktopServices.openUrl(QUrl(url))
                return
            except Exception:
                # fallback to local file URL
                pass
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    # ------------------------------------------------------------------
    # Helpers for wiring additional UI elements (place-holders)
    # ------------------------------------------------------------------
    def bind_open_button(self, button: QPushButton):
        """Wire an *Open* button to open the current html externally."""
        button.clicked.connect(self.open_current_external)

    def bind_selector(self, combo: QComboBox):
        """Populate selector with available visualisations and handle change."""
        def _refresh_items():
            combo.clear()
            for idx, path in enumerate(self.html_files):
                combo.addItem(f"#{idx} – {os.path.basename(path)}", userData=idx)
        _refresh_items()
        combo.currentIndexChanged.connect(lambda i: self.display_html(combo.currentData()))

    # ------------------------------------------------------------------
    # Qt event filter to capture double clicks anywhere inside container
    # ------------------------------------------------------------------
    def eventFilter(self, obj, event):  # type: ignore[override]
        if event.type() == QEvent.MouseButtonDblClick:
            self.open_current_external()
            return True  # swallow
        return super().eventFilter(obj, event)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _embed_html(self, file_path: str):
        container: QTextEdit = self.ui.visualisationTextEdit
        # Clean previous webviews
        for child in container.findChildren(QWebEngineView):
            child.setParent(None)
            child.deleteLater()

        webview = QWebEngineView(container)
        webview.setUrl(QUrl.fromLocalFile(file_path))

        rect: QRect = container.rect()
        webview.setGeometry(rect)
        webview.show()
        webview.setZoomFactor(0.8)

        # Also install event filter on the webview; this is more reliable
        # than monkey patching the mouseDoubleClickEvent, since the latter
        # might be swallowed by the internal page.
        webview.installEventFilter(self)

        # keep reference to avoid GC
        self._webview = webview 

    # ------------------------------------------------------------------
    # Optional configuration
    # ------------------------------------------------------------------
    def set_external_base_url(self, url: str):
        """Set a base http URL; when provided external open will use this instead of file:// paths.

        Example:  "http://127.0.0.1:5501/" (note trailing slash)
        """
        if not url.endswith('/'):
            url += '/'
        self.external_base_url = url 