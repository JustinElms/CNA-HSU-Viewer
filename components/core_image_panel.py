from pathlib import Path

import numpy as np
from natsort import os_sorted
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PySide6.QtGui import QColor, QPainter, QPixmap

from components.data_panel import DataPanel
from data.dataset import Dataset
from hsu_viewer.worker import Worker

"""
TODO
-add offset at top of panel
"""


class CoreImagePanel(DataPanel):
    def __init__(
        self,
        parent=None,
        threadpool=None,
        resolution: int = 0,
        dataset: Dataset = None,
        **kwargs,
    ) -> None:
        super().__init__(
            parent=parent,
            resolution=resolution,
            dataset=dataset,
            threadpool=threadpool,
            **kwargs,
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

        self.loading.emit(True)
        self.get_images()

    def get_images(self) -> None:
        if self.threadpool:
            worker = Worker(self._load_core_images)
            worker.signals.result.connect(self._display_core_images)
            worker.signals.finished.connect(self._on_finish)
            self.threadpool.start(worker)
        else:
            result = self._load_core_images()
            self._display_core_images(result)
            self.loading.emit(False)

    def _load_core_images(self) -> QWidget:
        pixmaps = []
        pixmap_width = 0

        match self.data_type:
            case "Spectral Images":
                self.meter = self.dataset.get_row_meter()
            case "Corebox Images":
                self.meter = self.dataset.get_box_meter()

        if self.meter.max() >= 9999:
            self.meter[:, 0] = np.arange(0, self.meter.shape[0], 1)
            self.meter[:, 1] = np.arange(1, self.meter.shape[0] + 1, 1)

        image_paths = os_sorted(
            Path(self.dataset_info.get("path")).glob("*.png")
        )
        total_image_height = 0

        for row_idx, path in enumerate(image_paths):
            pixmap = QPixmap(path)
            pixmap_height = np.rint(
                (self.meter[row_idx][1] - self.meter[row_idx][0])
                * self.resolution
            )
            pixmap = pixmap.scaledToHeight(pixmap_height)
            total_image_height = total_image_height + pixmap.height()
            if pixmap.width() > pixmap_width:
                pixmap_width = pixmap.width()

            pixmaps.append(pixmap)

        if self.meter[0, 0] != 0:
            self.meter = np.insert(
                self.meter.astype(float), 0, [0, self.meter[0, 0]], axis=0
            )

            pixmap_height = np.ceil(
                (self.meter[0][1] - self.meter[0][0]) * self.resolution
            )

            pixmap = QPixmap(pixmap_width, pixmap_height)

            qp = QPainter(pixmap)  # initiate painter
            qp.setBrush(QColor(0, 0, 0))  # paint meter background black
            qp.drawRect(0, 0, pixmap_width, pixmap_height)

            total_image_height = total_image_height + pixmap_height
            pixmaps.insert(0, pixmap)

        return pixmaps, pixmap_width, total_image_height

    def _display_core_images(self, result: tuple) -> None:
        pixmaps, pixmap_width, total_image_height = result

        self.clear_image_tiles()

        for pixmap in pixmaps:
            image = QLabel()
            image.setScaledContents(True)
            image.setPixmap(pixmap)
            self.insert_tile(image)

        self.image_frame_layout.setSpacing(0)
        self.image_frame_layout.setContentsMargins(0, 0, 0, 0)

        frame_height = (self.meter[-1][1] - self.meter[0][0]) * self.resolution
        frame_width = int(pixmap_width * frame_height / total_image_height)
        self.image_frame.setFixedSize(frame_width, frame_height)
        self.width = frame_width
        self.setFixedWidth(self.width)

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
        self.loading.emit(True)
        self.resolution = resolution
        self.get_images()
