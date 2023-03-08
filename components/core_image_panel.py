from pathlib import Path

import numpy as np
from natsort import os_sorted
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PySide6.QtGui import QPixmap

from components.data_panel import DataPanel


"""
TODO
-on resize enlarge current images while async get fresh copies at desired size
-add offset at top of panel
"""


class CoreImagePanel(DataPanel):
    def __init__(self, parent=None, resolution: int = 0, **kwargs) -> None:
        super().__init__(parent=parent, resolution=resolution, **kwargs)

        self.width = 0
        self.image_resolution = resolution

        image_frame = QWidget(self)
        self.image_frame_layout = QVBoxLayout(image_frame)
        # tooltip displays min name when hovering mouse over widget
        image_frame.setToolTip(f"{self.dataset} {self.dataname}")

        self.layout.addWidget(image_frame)

        self._load_core_images()

    def _load_core_images(self) -> QWidget:
        match self.datatype:
            case "Spectral Images":
                self.meter = self.config.get_row_meter(self.dataset)
            case "Corebox Images":
                self.meter = self.config.get_box_meter(self.dataset)

        if self.meter.min() >= 9999:
            self.meter[:, 0] = np.arange(0, self.meter.shape[0], 1)
            self.meter[:, 1] = np.arange(1, self.meter.shape[0] + 1, 1)

        data = self.config.data(
            self.dataset, self.datatype, self.datasubtype, self.dataname
        )

        image_dir = Path(data.get("path"))
        image_paths = os_sorted(image_dir.glob("*.png"))

        for index, path in enumerate(image_paths):
            pixmap = QPixmap(path)
            meter_depth = self.meter[index][1] - self.meter[index][0]
            pixel_depth = round(meter_depth * self.resolution)
            pixmap = pixmap.scaledToHeight(pixel_depth)
            if pixmap.width() > self.width:
                self.width = pixmap.width()
            image = QLabel()
            image.setScaledContents(True)
            image.setPixmap(pixmap)
            self.insert_tile(image)
            # self.image_frame_layout.addWidget(image, index, 1)

        self.image_frame_layout.setSpacing(0)
        self.image_frame_layout.setContentsMargins(0, 0, 0, 0)

    def insert_tile(self, tile: QLabel) -> None:
        if self.image_frame_layout.count() == 0:
            self.image_frame_layout.addWidget(tile)
            self.image_frame_layout.addStretch()
        else:
            self.image_frame_layout.insertWidget(
                self.image_frame_layout.count() - 1, tile
            )

    @Slot(int)
    def zoom_changed(self, resolution: int) -> None:
        self.resolution = resolution
        if (
            resolution / self.image_resolution < 3
            and resolution / self.image_resolution > 1 / 3
        ):
            for i in reversed(range(self.image_frame_layout.count() - 1)):
                meter_depth = self.meter[i][1] - self.meter[i][0]
                pixel_depth = round(meter_depth * self.resolution)
                widget = self.image_frame_layout.itemAt(i).widget()
                pixmap = widget.pixmap()
                widget.setPixmap(pixmap.scaledToHeight(pixel_depth))
        else:
            self.image_resolution = self.resolution
            for i in reversed(range(self.image_frame_layout.count() - 1)):
                try:
                    self.image_frame_layout.itemAt(i).widget().deleteLater()
                except AttributeError:
                    continue
            self._load_core_images()
