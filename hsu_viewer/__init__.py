from pathlib import Path

import matplotlib
from PySide6.QtGui import QIcon, QResizeEvent
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PySide6.QtCore import Signal, Slot
from static import icons

try:
    # Include in try/except block if you're also targeting Mac/Linux
    from ctypes import windll  # Only exists on Windows.

    myappid = "CNA.HSUViewer"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

from components.dashboard import Dashboard
from components.mineral_color_selector import MineralColorSelector

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

hsu_icons = icons


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
        images.
        """

        self.setStyleSheet(HSU_STYLES)
        self.setWindowIcon(QIcon(":/Icon.ico"))

        # set minimum size of app
        self.setMinimumSize(1000, 750)

        self.setWindowTitle("CNA HSU Viewer")

        # create main widget and layout
        self.main = QWidget(self)
        self.setCentralWidget(self.main)
        layout = QHBoxLayout(self.main)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        drawer = Drawer(self.main)

        self.dashboard = Dashboard(self.main, drawer.mineral_legend)
        drawer.zoom_in_button.clicked.connect(lambda: self.dashboard.zoom_in())
        drawer.zoom_out_button.clicked.connect(
            lambda: self.dashboard.zoom_out()
        )

        drawer.add_dataset_button.clicked.connect(self._open_dataset_selector)
        drawer.mineral_legend.color_clicked.connect(self._open_color_selector)
        self.dashboard.add_dataset_button.clicked.connect(
            self._open_dataset_selector
        )

        layout.addWidget(drawer)
        layout.addWidget(self.dashboard)

        # track which overlays/modals are open
        self.dataset_selector_open = False

        self.last_added = None

        # display app
        self.show()

    def resizeEvent(self, event: QResizeEvent) -> None:
        if self.dataset_selector_open:
            self.dataset_selector.resize(self.width(), self.height())

    def _open_dataset_selector(self) -> None:
        self.dataset_selector_open = True

        self.dataset_selector = DatasetSelector(
            self,
            config_path=Path.cwd().joinpath("hsu_datasets.cfg"),
            last_added=self.last_added,
        )
        self.dataset_selector.data_selected[dict].connect(self.add_data)
        self.dataset_selector.modal_closed.connect(
            self._close_dataset_selector
        )
        self.dataset_selector.show()

    def add_data(self, args: dict) -> None:
        self.last_added = args
        self.dashboard.add_data_panel(args)

    def _close_dataset_selector(self) -> None:
        self.dataset_selector = None
        self.dataset_selector_open = False

    @Slot(str, list)
    def _open_color_selector(self, mineral: str, colors: dict) -> None:
        color_selector = MineralColorSelector(self, mineral, colors)
        color_selector.show()
