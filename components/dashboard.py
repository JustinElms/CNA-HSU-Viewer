import numpy as np
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
)

from components.data_header import DataHeader
from components.core_image_panel import CoreImagePanel
from components.draggable_container import DraggableContainer
from components.meter import Meter
from components.spectral_plot_panel import SpectralPlotPanel

"""
TODO:
- docstrings
"""

METER_RES_LEVELS = {
    0: 5,
    1: 10,
    2: 15,
    3: 20,
    4: 25,
    5: 30,
    6: 35,
    7: 40,
    8: 45,
    9: 50,
}


class Dashboard(QScrollArea):
    zoom_changed = Signal(int)
    meter_changed = Signal(float, int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.zoom_level = 0

        layout = QVBoxLayout(self)

        header_content = QWidget()
        header_content.setFixedHeight(60)

        header_spacer = QWidget()
        header_spacer.setFixedWidth(60)
        self.header_container = DraggableContainer(self)

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
        data_content_layout = QHBoxLayout(data_content)
        data_content_layout.setSpacing(0)
        data_content_layout.setContentsMargins(0, 0, 0, 0)

        self.data_container = DraggableContainer(data_content)

        self.header_container.widget_dragged.connect(
            self.data_container.insert_dragged_widget
        )

        resolution = METER_RES_LEVELS[self.zoom_level]

        self.meter_max = 0
        self.meter_height = 669

        self.meter = Meter(
            data_content, resolution, self.meter_height, self.meter_max
        )
        self.meter.setFixedWidth(60)
        self.zoom_changed.connect(self.meter.zoom_changed)
        self.meter_changed.connect(self.meter.update_size)

        data_content_layout.addWidget(self.meter)
        data_content_layout.addWidget(self.data_container)

        data_content_scroll = QScrollArea(self)
        data_content_scroll.setWidget(data_content)
        data_content_scroll.setWidgetResizable(True)
        data_content_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        data_content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.viewport = data_content_scroll.viewport()

        layout.addWidget(header_content)
        layout.addWidget(data_content_scroll)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setStyleSheet("background-color: rgb(0,0,0)")

    def add_data_panel(self, kwargs: dict) -> None:
        meter_end = kwargs.get("meter_end")
        if meter_end > self.meter_max:
            self.meter_max = meter_end
        meter_height = self.viewport.height()
        self.meter_changed.emit(self.meter_max, meter_height)

        match kwargs.get("datatype"):
            case "Spectral Images":
                panel = CoreImagePanel(
                    self.data_container,
                    METER_RES_LEVELS[self.zoom_level],
                    **kwargs
                )
            case "Corebox Images":
                panel = CoreImagePanel(
                    self.data_container,
                    METER_RES_LEVELS[self.zoom_level],
                    **kwargs
                )
            case "Spectral Data":
                panel = SpectralPlotPanel(
                    self.data_container,
                    METER_RES_LEVELS[self.zoom_level],
                    **kwargs
                )
        header = DataHeader(self.header_container, panel.width, **kwargs)
        self.zoom_changed.connect(panel.zoom_changed)
        panel.resize_panel.connect(header.resize_header)
        header.close_panel.connect(panel.close_panel)

        self.header_container.insert_panel(header)
        self.data_container.insert_panel(panel)

    def zoom_in(self) -> None:
        if self.zoom_level < 9:
            self.zoom_level += 1
            self.zoom_changed.emit(METER_RES_LEVELS[self.zoom_level])

    def zoom_out(self) -> None:
        if self.zoom_level > 0:
            self.zoom_level -= 1
            self.zoom_changed.emit(METER_RES_LEVELS[self.zoom_level])

    def resizeEvent(self, event: QResizeEvent) -> None:
        meter_height = self.viewport.height()
        max_depth = self._max_panel_depth()
        self.meter_changed.emit(max_depth, meter_height)
        # if meter_height == 0:
        #     depth = self.height() - 60
        # depth = round((meter_height) / (resolution * 10)) * 10
        # if depth > self.meter_max:
        #     self.meter_max = depth
        #     self.meter_changed.emit(max_depth, meter_height)

    def _max_panel_depth(self) -> float:
        depths = []
        for i in range(self.data_container.layout.count() - 1):
            depths.append(self.data_container.layout.itemAt(i).widget().depth)
        if not depths:
            return 0
        return np.max(depths)
