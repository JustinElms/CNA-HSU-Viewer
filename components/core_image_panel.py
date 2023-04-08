from pathlib import Path

import numpy as np
from natsort import os_sorted
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PySide6.QtGui import QPixmap

from components.data_panel import DataPanel
from data.dataset import Dataset

"""
TODO
-on resize enlarge current images while async get fresh copies at desired size
-add offset at top of panel
"""


class CoreImagePanel(DataPanel):
    def __init__(
        self,
        parent=None,
        resolution: int = 0,
        dataset: Dataset = None,
        **kwargs,
    ) -> None:
        super().__init__(
            parent=parent, resolution=resolution, dataset=dataset, **kwargs
        )

        self.width = 0
        self.image_resolution = resolution
        self.depth = dataset.meter_end()

        self.image_frame = QWidget(self)
        self.image_frame_layout = QVBoxLayout(self.image_frame)
        # tooltip displays min name when hovering mouse over widget
        self.image_frame.setToolTip(f"{self.dataset_name} {self.data_name}")

        self.layout.addWidget(self.image_frame)
        self.layout.addStretch()

        self._load_core_images()

    def _load_core_images(self) -> QWidget:
        match self.data_type:
            case "Spectral Images":
                self.meter = self.dataset.get_row_meter()
            case "Corebox Images":
                self.meter = self.dataset.get_box_meter()

        if self.meter.min() >= 9999:
            self.meter[:, 0] = np.arange(0, self.meter.shape[0], 1)
            self.meter[:, 1] = np.arange(1, self.meter.shape[0] + 1, 1)

        image_paths = os_sorted(
            Path(self.dataset_info.get("path")).glob("*.png")
        )
        total_image_height = 0

        for path in image_paths:
            pixmap = QPixmap(path)
            total_image_height = total_image_height + pixmap.height()
            if pixmap.width() > self.width:
                new_width = pixmap.width()
            image = QLabel()
            image.setScaledContents(True)
            image.setPixmap(pixmap)
            self.insert_tile(image)

        self.image_frame_layout.setSpacing(0)
        self.image_frame_layout.setContentsMargins(0, 0, 0, 0)

        frame_height = (self.meter[-1][1] - self.meter[0][0]) * self.resolution
        frame_width = int(new_width * frame_height / total_image_height)
        self.image_frame.setFixedSize(frame_width, frame_height)
        self.width = frame_width

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
        zoom_ratio = resolution / self.resolution
        new_height = np.floor(self.image_frame.height() * zoom_ratio)
        new_width = np.floor(self.image_frame.width() * zoom_ratio)
        self.image_frame.setFixedSize(new_width, new_height)
        self.width = new_width
        self.resolution = resolution
