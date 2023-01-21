from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QScrollArea,
)

from components.data_header import DataHeader
from components.data_panel import DataPanel
from components.draggable_container import DraggableContainer
from components.meter import Meter


class Dashboard(QScrollArea):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.zoom_level = 0

        layout = QVBoxLayout(self)

        header_content = QWidget()
        header_content.setFixedHeight(60)

        header_spacer = QWidget()
        header_spacer.setFixedWidth(60)
        self.header_container = DraggableContainer(self)
        self.header_container.setStyleSheet("background-color: purple")

        header_scroll = QScrollArea(self)
        header_scroll.setWidget(self.header_container)
        header_scroll.setWidgetResizable(True)
        header_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        header_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        header_scroll.setFixedHeight(60)

        header_content_layout = QHBoxLayout(header_content)
        header_content_layout.setSpacing(0)
        header_content_layout.setContentsMargins(0, 0, 0, 0)
        header_content_layout.addWidget(header_spacer)
        header_content_layout.addWidget(header_scroll)

        # create area to display data
        data_content = QWidget()
        data_content.setStyleSheet("background-color: green;")
        data_content_layout = QHBoxLayout(data_content)
        data_content_layout.setSpacing(0)
        data_content_layout.setContentsMargins(0, 0, 0, 0)
        data_content.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        )

        self.meter = Meter(data_content, self.zoom_level)
        self.meter.setFixedWidth(60)
        self.meter.setStyleSheet("background-color: green")

        self.data_container = DraggableContainer(data_content)

        self.header_container.widget_dragged.connect(
            self.data_container.insert_dragged_widget
        )

        data_content_layout.addWidget(self.meter)
        data_content_layout.addWidget(self.data_container)

        data_content_scroll = QScrollArea(self)
        data_content_scroll.setWidget(data_content)
        data_content_scroll.setWidgetResizable(True)
        data_content_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        data_content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        layout.addWidget(header_content)
        layout.addWidget(data_content_scroll)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.test_add_panel()

    def add_data_panel(self, kwargs: dict) -> None:

        dataset = kwargs.get("dataset")
        datatype = kwargs.get("datatype")
        datasubtype = kwargs.get("datasubtype")
        dataname = kwargs.get("dataname")

        panel = DataPanel(self.data_container, **kwargs)
        header = DataHeader(
            self.header_container, dataset, dataname, panel.width
        )

        self.header_container.insert_panel(header)
        self.data_container.insert_panel(panel)

    def test_add_panel(self):
        # kwargs = {
        #     "dataset": "PB-77-013",
        #     "datatype": "Spectral Images",
        #     "datasubtype": "Chemistry",
        #     "dataname": "Biotite",
        # }
        kwargs = {
            "dataset": "PB-77-013",
            "datatype": "Corebox Images",
            "datasubtype": "High-Res",
            "dataname": "High-Res",
        }
        self.add_data_panel(kwargs)
