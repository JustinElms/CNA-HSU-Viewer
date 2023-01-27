from pathlib import Path

from natsort import os_sorted
from PySide6.QtCore import Slot
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
    QGridLayout,
)
from PySide6.QtGui import QPixmap


from hsu_viewer.dataset_config import DatasetConfig


class DataPanel(QWidget):
    def __init__(self, parent=None, resolution: int = 0, **kwargs) -> None:
        super().__init__(parent=parent)

        self.resolution = resolution
        self.width = 0

        self.dataset = kwargs.get("dataset")
        self.datatype = kwargs.get("datatype")
        self.datasubtype = kwargs.get("datasubtype")
        self.dataname = kwargs.get("dataname")

        self.config = DatasetConfig(Path.cwd().joinpath("hsu_datasets.cfg"))

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.load_data()

    def load_data(self) -> None:
        match self.datatype:
            case "Spectral Images":
                self.meter = self.config.get_row_meter(self.dataset)
                data = self._load_core_images()
            case "Corebox Images":
                self.meter = self.config.get_box_meter(self.dataset)
                data = self._load_core_images()

        self.layout.addWidget(data)

    def _load_core_images(self) -> QWidget:
        data = self.config.data(
            self.dataset, self.datatype, self.datasubtype, self.dataname
        )

        image_dir = Path(data.get("path"))
        image_paths = os_sorted(image_dir.glob("*.png"))

        image_frame = QWidget(self)
        image_frame.setStyleSheet("background-color: white;")
        self.image_frame_layout = QGridLayout(image_frame)

        for index, path in enumerate(image_paths):
            pixmap = QPixmap(path)
            meter_depth = self.meter[index][1] - self.meter[index][0]
            pixel_depth = round(meter_depth * self.resolution)
            pixmap = pixmap.scaledToHeight(pixel_depth)
            if pixmap.width() > self.width:
                self.width = pixmap.width()
            image = QLabel(image_frame)
            image.setScaledContents(True)
            image.setPixmap(pixmap)
            self.image_frame_layout.addWidget(image, index, 1)

        self.image_frame_layout.setSpacing(0)
        self.image_frame_layout.setContentsMargins(0, 0, 0, 0)
        # tooltip displays min name when hovering mouse over widget
        image_frame.setToolTip("title")

        return image_frame

    @Slot(int)
    def zoom_changed(self, resolution: int) -> None:
        self.resolution = resolution
        for i in reversed(range(self.image_frame_layout.count())):
            meter_depth = self.meter[i][1] - self.meter[i][0]
            pixel_depth = round(meter_depth * self.resolution)
            widget = self.image_frame_layout.itemAt(i).widget()
            pixmap = widget.pixmap()
            widget.setPixmap(pixmap.scaledToHeight(pixel_depth))

    def resizeEvent(self, event: QResizeEvent) -> None:
        return super().resizeEvent(event)
