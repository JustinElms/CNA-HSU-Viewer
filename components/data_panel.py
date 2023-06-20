from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

import numpy as np

from data.dataset import Dataset
from components.loading_panel import LoadingPanel


class DataPanel(QWidget):
    resize_header = Signal(int)
    resize_spinner = Signal(int, int)
    loading = Signal(bool)

    def __init__(
        self,
        parent=None,
        threadpool=None,
        resolution: int = 0,
        dataset: Dataset = None,
        **kwargs
    ) -> None:
        super().__init__(parent=parent)

        self.threadpool = threadpool
        self.resolution = resolution
        self.dataset = dataset
        self.dataset_name = kwargs.get("dataset_name")
        self.data_type = kwargs.get("data_type")
        self.data_subtype = kwargs.get("data_subtype")
        self.data_name = kwargs.get("data_name")
        self.dataset_info = dataset.data(
            self.data_type, self.data_subtype, self.data_name
        )
        self.csv_data = self.dataset.config["csv_data"]

        self.loading_panel = LoadingPanel(self)
        self.loading_panel.raise_()
        self.resize_spinner.connect(self.loading_panel.resize_panel)
        self.loading.connect(self.set_loading)

        self.setFixedWidth(120)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    @Slot()
    def close_panel(self) -> None:
        self.deleteLater()

    @Slot(bool)
    def set_loading(self, show_spinner) -> None:
        self.loading_panel.raise_()
        if show_spinner:
            self.loading_panel.show()
        else:
            self.loading_panel.hide()

    @Slot()
    def _on_finish(self) -> None:
        self.loading.emit(False)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.resize_header.emit(self.geometry().width())
        self.resize_spinner.emit(self.width, self.parent().height())

    def hex_to_rgb(self, hex):
        return np.array([int(hex[i: i + 2], 16) for i in (0, 2, 4)])

    def composite_tooltip(self, plot_colors: dict) -> str:
        tag = ""
        for idx, mineral in enumerate(self.data_name):
            tag = (
                tag
                + '<font color="'
                + plot_colors.get(mineral)
                + '">■</font> '
                + mineral
            )
            if idx != len(self.data_name) - 1:
                tag = tag + "<br>"
        return tag

    def clear_image_tiles(self) -> None:
        for i in reversed(range(self.image_frame_layout.count())):
            item = self.image_frame_layout.itemAt(i)
            if not isinstance(item, QSpacerItem):
                item.widget().setVisible(False)
                item.widget().deleteLater()
