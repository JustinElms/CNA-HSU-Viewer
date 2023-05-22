from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
)

import numpy as np

from data.dataset import Dataset


class DataPanel(QWidget):
    resize_panel = Signal(int)

    def __init__(
        self,
        parent=None,
        resolution: int = 0,
        dataset: Dataset = None,
        **kwargs
    ) -> None:
        super().__init__(parent=parent)

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

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    @Slot()
    def close_panel(self) -> None:
        self.deleteLater()

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.resize_panel.emit(self.geometry().width())

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
