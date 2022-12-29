from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QScrollArea,
)

from components.draggable_container import DraggableContainer
from components.meter import Meter


class Dashboard(QScrollArea):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)

        self.header_container = DraggableContainer(self)
        self.header_container.setStyleSheet("background-color: purple")

        header_scroll = QScrollArea(self)
        header_scroll.setWidget(self.header_container)
        header_scroll.setWidgetResizable(True)
        header_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        header_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        header_scroll.setFixedHeight(60)

        # create area to display data
        content = QWidget()
        content.setStyleSheet("background-color: white;")
        content_layout = QHBoxLayout(content)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))

        self.meter = Meter(content)
        self.meter.setFixedWidth(60)
        self.meter.setStyleSheet("background-color: green")
        self.data_container = DraggableContainer(content)
        self.data_container.setStyleSheet("background-color: blue")

        content_layout.addWidget(self.meter)
        content_layout.addWidget(self.data_container)

        content_scroll = QScrollArea(self)
        content_scroll.setWidget(content)
        content_scroll.setWidgetResizable(True)
        content_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        layout.addWidget(header_scroll)
        layout.addWidget(content_scroll)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
