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
        data_content.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))

        self.meter = Meter(data_content)
        self.meter.setFixedWidth(60)
        self.meter.setStyleSheet("background-color: green")
        
        self.data_container = DraggableContainer(data_content)

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

        self.test_data_widget()

    def test_data_widget(self):
        # self.data_container.add_data_panel()
        panel = DataPanel(self.data_container, self.meter.geometry().height(), "test1")  # dataset, datatype, subtype, data)
        header = DataHeader(self.header_container, "test1")
        header.header_drag.connect(lambda: panel.drag_event())
        self.data_container.insert_panel(panel)
        self.header_container.insert_panel(header)

        panel2 = DataPanel(self.data_container, self.meter.geometry().height(), "test2")  # dataset, datatype, subtype, data)
        header2 = DataHeader(self.header_container, "test2")
        header2.header_drag.connect(lambda: panel2.drag_event())
        self.data_container.insert_panel(panel2)
        self.header_container.insert_panel(header2)

        panel3 = DataPanel(self.data_container, self.meter.geometry().height(), "test3")  # dataset, datatype, subtype, data)
        header3 = DataHeader(self.header_container, "test3")
        header3.header_drag.connect(lambda: panel2.drag_event())
        self.data_container.insert_panel(panel3)
        self.header_container.insert_panel(header3)          
