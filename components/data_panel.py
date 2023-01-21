from pathlib import Path

from natsort import os_sorted
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
    QGridLayout,
)
from PySide6.QtGui import QPixmap


from hsu_viewer.dataset_config import DatasetConfig

# resolution of each zoom level, zoom level: px/m
METER_RES_LEVELS = {
    0: 10,
    1: 20,
    2: 40,
    3: 60,
    4: 80,
    5: 100,
}


class DataPanel(QWidget):
    def __init__(self, parent=None, zoom_level: int = 0, **kwargs) -> None:
        super().__init__(parent=parent)

        self.zoom_level = zoom_level
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

        data = self.load_data()

        self.layout.addWidget(data)

    def load_data(self) -> None:
        match self.datatype:
            case "Spectral Images":
                data = self._load_core_images()
            case "Corebox Images":
                data = self._load_core_images()

        return data

    def _load_core_images(self) -> QWidget:
        data = self.config.data(
            self.dataset, self.datatype, self.datasubtype, self.dataname
        )

        image_dir = Path(data.get("path"))
        image_paths = os_sorted(image_dir.glob("*.png"))
        meter = self.config.meter(self.dataset)
        coreFrame = QWidget(self)
        coreFrame.setStyleSheet("background-color: white;")
        coreFrameLayout = QGridLayout(coreFrame)

        for index, path in enumerate(image_paths):
            pixmap = QPixmap(path)
            meter_depth = meter[index][1] - meter[index][0]
            pixel_depth = round(
                meter_depth * METER_RES_LEVELS[self.zoom_level]
            )
            pixmap = pixmap.scaledToHeight(pixel_depth)
            if pixmap.width() > self.width:
                self.width = pixmap.width()
            coreIm = QLabel(coreFrame)
            coreIm.setScaledContents(True)
            coreIm.setPixmap(pixmap)
            coreFrameLayout.addWidget(coreIm, index, 1)

        coreFrameLayout.setSpacing(0)
        coreFrameLayout.setContentsMargins(0, 0, 0, 0)
        # tooltip displays min name when hovering mouse over widget
        coreFrame.setToolTip("title")

        return coreFrame
