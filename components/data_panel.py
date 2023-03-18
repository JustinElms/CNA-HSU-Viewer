from pathlib import Path

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
)

from hsu_viewer.dataset_config import DatasetConfig


class DataPanel(QWidget):
    resize_panel = Signal(int)

    def __init__(self, parent=None, resolution: int = 0, **kwargs) -> None:
        super().__init__(parent=parent)

        self.resolution = resolution
        self.dataset = kwargs.get("dataset")
        self.datatype = kwargs.get("datatype")
        self.datasubtype = kwargs.get("datasubtype")
        self.dataname = kwargs.get("dataname")

        self.config = DatasetConfig(Path.cwd().joinpath("hsu_datasets.cfg"))

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    @Slot()
    def close_panel(self) -> None:
        self.deleteLater()

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.resize_panel.emit(self.geometry().width())
