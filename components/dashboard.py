from PySide6.QtCore import QPoint, QRect, Qt, Signal, Slot, QThreadPool
from PySide6.QtGui import QResizeEvent, QPixmap, QIcon
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QScrollArea,
)

from components.data_header import DataHeader
from components.composite_image_panel import CompositeImagePanel
from components.composite_plot_panel import CompositePlotPanel
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

    def __init__(self, parent=None, mineral_legend: QWidget = None) -> None:
        super().__init__(parent)

        self.threadpool = QThreadPool()

        self.zoom_level = 0
        self.mineral_legend = mineral_legend
        self.colormap = {}

        layout = QGridLayout(self)

        resolution = METER_RES_LEVELS[self.zoom_level]
        self.meter_height = 0

        self.meter = Meter(self, resolution, self.meter_height, 0)
        self.meter.setFixedWidth(60)
        self.zoom_changed.connect(self.meter.zoom_changed)
        self.meter_changed.connect(self.meter.update_size)

        meter_scroll = QScrollArea(self)
        meter_scroll.setWidget(self.meter)
        meter_scroll.setWidgetResizable(True)
        meter_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        meter_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        meter_scroll.setFixedWidth(60)

        header_content = QWidget()
        header_content.setFixedHeight(80)

        self.header_container = DraggableContainer(self, header=True)

        header_scroll = QScrollArea(self)
        header_scroll.setWidget(self.header_container)
        header_scroll.setWidgetResizable(True)
        header_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        header_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        header_scroll.setFixedHeight(80)

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

        data_content_layout.addWidget(self.data_container)

        data_content_scroll = QScrollArea(self)
        data_content_scroll.setWidget(data_content)
        data_content_scroll.setWidgetResizable(True)
        data_content_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        data_content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        data_content_scroll.horizontalScrollBar().valueChanged.connect(
            header_scroll.horizontalScrollBar().setValue
        )

        # sync scrollbars for various QScrollAreas
        data_content_scroll.verticalScrollBar().valueChanged.connect(
            meter_scroll.verticalScrollBar().setValue
        )
        meter_scroll.verticalScrollBar().valueChanged.connect(
            data_content_scroll.verticalScrollBar().setValue
        )

        data_content_scroll.horizontalScrollBar().valueChanged.connect(
            header_scroll.horizontalScrollBar().setValue
        )
        header_scroll.horizontalScrollBar().valueChanged.connect(
            data_content_scroll.horizontalScrollBar().setValue
        )

        self.add_dataset_button = QPushButton(self)
        self.add_dataset_button.setIcon(QIcon(QPixmap(":/plus.svg")))
        self.add_dataset_button.setFixedSize(50, 50)
        self.add_dataset_button.raise_()
        self.add_dataset_button.setToolTip("Add Data Panel")
        self.add_dataset_button.setStyleSheet(
            """
            QToolTip {background-color: black;}
            color: white;
            background-color: green;
            border-radius : 25;
            border: 2px solid white"""
        )

        self.viewport = data_content_scroll.viewport()

        layout.addWidget(meter_scroll, 1, 0)
        layout.addWidget(header_content, 0, 1)
        layout.addWidget(data_content_scroll, 1, 1)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setStyleSheet("background-color: rgb(0,0,0)")

    @Slot(dict)
    def add_data_panel(self, dataset_args: dict) -> None:
        dataset_config = dataset_args.get("config")
        dataset_args.pop("config")
        meter_end = dataset_config.meter_end()

        self.mineral_legend.add_minerals(dataset_args.get("data_name"))
        plot_colors = self.mineral_legend.color(dataset_args.get("data_name"))

        if meter_end > self.data_container.max_panel_depth():
            meter_height = self.viewport.height()
            self.meter_changed.emit(meter_end, meter_height)

        match dataset_args.get("data_type"):
            case "Spectral Images":
                if dataset_args.get("data_subtype") == "Composite Images":
                    panel = CompositeImagePanel(
                        self.data_container,
                        self.threadpool,
                        METER_RES_LEVELS[self.zoom_level],
                        dataset_config,
                        plot_colors,
                        **dataset_args,
                    )
                else:
                    panel = CoreImagePanel(
                        self.data_container,
                        self.threadpool,
                        METER_RES_LEVELS[self.zoom_level],
                        dataset_config,
                        **dataset_args,
                    )
            case "Corebox Images":
                panel = CoreImagePanel(
                    self.data_container,
                    self.threadpool,
                    METER_RES_LEVELS[self.zoom_level],
                    dataset_config,
                    **dataset_args,
                )
            case "Spectral Data":
                if dataset_args.get("data_subtype") == "Composite Plot":
                    panel = CompositePlotPanel(
                        self.data_container,
                        self.threadpool,
                        METER_RES_LEVELS[self.zoom_level],
                        dataset_config,
                        plot_colors,
                        **dataset_args,
                    )
                else:
                    panel = SpectralPlotPanel(
                        self.data_container,
                        self.threadpool,
                        METER_RES_LEVELS[self.zoom_level],
                        dataset_config,
                        plot_colors,
                        **dataset_args,
                    )

        header = DataHeader(
            self.header_container, panel.width, dataset_config, **dataset_args
        )

        image_height = int(
            (dataset_config.meter_end() - dataset_config.meter_start())
            * METER_RES_LEVELS[self.zoom_level]
        )

        self.zoom_changed.connect(panel.zoom_changed)
        panel.resize_header.connect(header.resize_header)
        if dataset_args.get("data_subtype") == "Composite Plot":
            panel.update_axis_limits.connect(header.update_axis_limits)
        header.close_panel.connect(panel.close_panel)
        header.close_panel.connect(
            lambda: self.remove_legend_mineral(dataset_args["data_name"])
        )

        if dataset_args.get("data_subtype") not in [
            "Composite Images",
            "Composite Plot",
        ]:
            image_name = (
                "_".join(dataset_args.values()).replace(" ", "_") + ".png"
            )
        else:
            image_name = (
                "_".join(
                    [
                        dataset_args.get("dataset_name"),
                        dataset_args.get("data_subtype"),
                        *dataset_args.get("data_name"),
                    ]
                ).replace(" ", "_")
                + ".png"
            )
        panel_image = panel.grab(
            QRect(QPoint(0, 0), QPoint(panel.width, image_height))
        )
        header.save_image.connect(
            lambda: self.save_panel_image(panel_image, image_name)
        )

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
        self.add_dataset_button.move(self.width() - 85, self.height() - 85)

    def remove_legend_mineral(self, closed_minerals: str | list) -> None:
        if not isinstance(closed_minerals, list):
            closed_minerals = [closed_minerals]

        mineral_list = self.data_container.get_current_minerals()

        for mineral in closed_minerals:
            if mineral_list.count(mineral) == 1:
                self.mineral_legend.remove_mineral(mineral)

    def save_panel_image(
        self,
        panel_image: QPixmap,
        image_name: str,
    ) -> None:
        meter_image = self.meter.grab(
            QRect(
                QPoint(0, 0), QPoint(self.meter.width(), panel_image.height())
            )
        )
        save_panel_window = SavePanelWindow(
            self.parent(), panel_image, meter_image, image_name
        )
        save_panel_window.show()
