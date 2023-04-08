from PySide6.QtCore import QPoint, QRect, Qt, Signal, Slot
from PySide6.QtGui import QResizeEvent, QPixmap
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
from components.save_panel_window import SavePanelWindow
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

        self.header_container = DraggableContainer(self, header=True)

        header_scroll = QScrollArea(self)
        header_scroll.setWidget(self.header_container)
        header_scroll.setWidgetResizable(True)
        header_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        header_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        header_scroll.setFixedHeight(60)

        header_content_layout = QHBoxLayout(header_content)
        header_content_layout.setSpacing(0)
        header_content_layout.setContentsMargins(0, 0, 0, 0)
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
        self.meter_height = 0

        self.meter = Meter(data_content, resolution, self.meter_height, 0)
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

        data_content_scroll.horizontalScrollBar().valueChanged.connect(
            header_scroll.horizontalScrollBar().setValue
        )

        self.viewport = data_content_scroll.viewport()

        layout.addWidget(header_content)
        layout.addWidget(data_content_scroll)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setStyleSheet("background-color: rgb(0,0,0)")

    @Slot(dict)
    def add_data_panel(self, dataset_args: dict) -> None:
        dataset_config = dataset_args.get("config")
        dataset_args.pop("config")
        meter_end = dataset_config.meter_end()
        if meter_end > self.data_container.max_panel_depth():
            meter_height = self.viewport.height()
            self.meter_changed.emit(meter_end, meter_height)

        match dataset_args.get("data_type"):
            case "Spectral Images":
                panel = CoreImagePanel(
                    self.data_container,
                    METER_RES_LEVELS[self.zoom_level],
                    dataset_config,
                    **dataset_args,
                )
            case "Corebox Images":
                panel = CoreImagePanel(
                    self.data_container,
                    METER_RES_LEVELS[self.zoom_level],
                    dataset_config,
                    **dataset_args,
                )
            case "Spectral Data":
                panel = SpectralPlotPanel(
                    self.data_container,
                    METER_RES_LEVELS[self.zoom_level],
                    dataset_config,
                    **dataset_args,
                )

        header = DataHeader(
            self.header_container, panel.width, dataset_config, **dataset_args
        )

        image_height = int(
            (dataset_config.meter_end() - dataset_config.meter_start())
            * METER_RES_LEVELS[self.zoom_level]
        )
        image_name = "_".join(dataset_args.values()) + ".png"
        panel_image = panel.grab(
            QRect(QPoint(0, 0), QPoint(panel.width, image_height))
        )
        meter_image = self.meter.grab(
            QRect(QPoint(0, 0), QPoint(60, image_height))
        )
        header.save_image.connect(
            lambda: self.save_panel_image(
                panel_image, meter_image, image_name
            )
        )
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
        self.meter_height = self.viewport.height()
        if self.meter_height < 669:
            self.meter_height = 669
        max_depth = self.data_container.max_panel_depth()
        self.meter_changed.emit(max_depth, self.meter_height)

    def save_panel_image(
        self,
        panel_image: QPixmap,
        meter_image: QPixmap,
        image_name: str,
    ) -> None:
        save_panel_window = SavePanelWindow(
            self.parent(), panel_image, meter_image, image_name
        )
        save_panel_window.show()
