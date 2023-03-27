import os
from pathlib import Path

import matplotlib
from PySide6.QtGui import QIcon, QScreen, QResizeEvent
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QApplication
from PySide6.QtCore import Signal

try:
    # Include in try/except block if you're also targeting Mac/Linux
    from ctypes import windll  # Only exists on Windows.

    myappid = "CNA.HSUViewer"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

from components.dashboard import Dashboard

# from components.data_widget import DataWidget
from components.dataset_selector import DatasetSelector
from components.drawer import Drawer

matplotlib.use("QtAgg")

HSU_STYLES = """
    QWidget{
        background-color: rgb(10,15,20);
        color: rgb(222, 222, 222)
    }
    QWidget#drawer{
        background-color: rgb(10,15,20);
        border: 1px transparent;
        color: rgb(222, 222, 222)
    }
    QToolTip{
        background-color: rgb(10,15,20);
        border: 1px solid rgb(222, 222, 222);
        color: rgb(222, 222, 222)
    }

    QMainWindow{
        background-color: rgb(10,15,20);
        border: 1px transparent;
        color: rgb(222, 222, 222)
    }

    QGroupBox#drawer{
        background-color: rgb(10,15,20);
        border: 1px solid rgb(222,222,222);
        margin-top: 0.5em;
    }

    QGroupBox#drawer::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 3px 0 3px;
    }
"""


class HSUViewer(QMainWindow):
    """
    mainWindow is the main class of the application.
    main window consists of an options drawer, down-hole meter, and data area
    (dashboard) two overlays are used to display data headers and a depth
    marker on top of the data area.
    """

    # Signal for when a minerals color is changed
    minColorChanged = Signal()
    # Signal for when zoom level is changed
    zoomChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        """
        initializes widget sylesheets, image sizes, and lists of minerals and
        images. Calls self.initUI() to create widgets
        """

        self.setStyleSheet(HSU_STYLES)

        # save the apps root directory for future reference
        self.rootDir = os.getcwd()
        screenGeometry = QScreen.availableGeometry(
            QApplication.primaryScreen()
        )  # gets screen resolution
        self.meterWidth = 60
        self.startHeight = screenGeometry.height() - 60
        self.dataWidgetHeight = self.startHeight
        self.startWidth = []
        self.dataWidgetWidth = (
            []
        )  # initialize variable, gets corrected when data is loaded

        self.setWindowIcon(QIcon(":/Icon.ico"))

        # set minimum size of app
        self.setMinimumSize(1000, 750)

        # initialize app widgets
        self.initUI()

        # track which overlays/modals are open
        self.dataset_selector_open = False

        # display app
        self.show()

    def initUI(self) -> None:
        """
        initUI creates the widgets for the application
        """

        os.chdir(self.rootDir)
        self.setWindowTitle("CNA Core Viewer")

        # create main widget and layout
        self.main = QWidget(self)
        self.setCentralWidget(self.main)
        mainLayout = QHBoxLayout(self.main)
        mainLayout.setSpacing(0)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        drawer = Drawer(self.main)

        self.dashboard = Dashboard(self.main)
        drawer.zoom_in_button.clicked.connect(lambda: self.dashboard.zoom_in())
        drawer.zoom_out_button.clicked.connect(
            lambda: self.dashboard.zoom_out()
        )

        drawer.add_dataset_button.clicked.connect(self._open_dataset_selector)

        mainLayout.addWidget(drawer)
        mainLayout.addWidget(self.dashboard)

    def resizeEvent(self, event: QResizeEvent) -> None:
        if self.dataset_selector_open:
            self.dataset_selector.resize(self.width(), self.height())

    def _open_dataset_selector(self) -> None:

        self.dataset_selector_open = True

        self.dataset_selector = DatasetSelector(
            self, config_path=Path.cwd().joinpath("hsu_datasets.cfg")
        )
        self.dataset_selector.data_selected.connect(self.dashboard.add_data_panel)
        self.dataset_selector.modal_closed.connect(self._close_dataset_selector)
        self.dataset_selector.show()

    def _close_dataset_selector(self) -> None:
        self.dataset_selector = None
        self.dataset_selector_open = False

    def _add_data(self, kwargs) -> None:
        self.dashboard.add_data_panel(kwargs)
