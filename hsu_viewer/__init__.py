import os
from pathlib import Path

import matplotlib
import numpy as np
from PySide6.QtGui import QIcon, QScreen
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QApplication
from PySide6. QtCore import Qt, Signal, Slot

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
from components.overlay_view import *
from plotters.drawing import *
from static.resources import *

matplotlib.use("tkagg")

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

DEFAULT_COLORS = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]


class HSUViewer(QMainWindow):
    """
    mainWindow is the main class of the application.
    main window consists of an options drawer, down-hole meter, and data area (dashboard)
    two overlays are used to display data headers and a depth marker on top of the data
    area
    """

    # Signal for when a minerals color is changed
    minColorChanged = Signal()
    # Signal for when zoom level is changed
    zoomChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        """
        initializes widget sylesheets, image sizes, and lists of minerals and images.
        calls self.initUI() to create widgets
        """

        self.setStyleSheet(HSU_STYLES)

        self.rootDir = os.getcwd()  # save the apps root directory for future reference
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
        self.imDict = []

        # intialize lists for data, mineral names, and images
        self.minMeter = []

        # default colors for minerals in plots and overlay
        self.defaultColors = DEFAULT_COLORS
        self.plotColors = self.defaultColors.copy()
        self.setWindowIcon(QIcon(":/Icon.ico"))

        # set minimum size of app
        self.setMinimumSize(1000, 750)

        # initialize app widgets
        self.initUI()

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

        drawer.add_dataset_button.clicked.connect(self._open_dataset_selector)

        mainLayout.addWidget(drawer)
        mainLayout.addWidget(self.dashboard)


    def _open_dataset_selector(self) -> None:

        data_selector = DatasetSelector(
            self, config_path=Path.cwd().joinpath("hsu_datasets.cfg")
        )
        data_selector.data_selected.connect(self._add_data)
        data_selector.show()

    def _add_data(self, dataset, datatype, subtype, data) -> None:
        self.dashboard.data_container.add_data_panel(
            dataset, datatype, subtype, data
        )
