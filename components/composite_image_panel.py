from pathlib import Path

import numpy as np
from natsort import os_sorted
from PIL import Image, ImageQt
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PySide6.QtGui import QPixmap

from components.data_panel import DataPanel
from data.dataset import Dataset
from hsu_viewer.worker import Worker

"""
TODO
-add offset at top of panel
-increase brightness
"""


class CompositeImagePanel(DataPanel):
    def __init__(
        self,
        parent=None,
        threadpool=None,
        resolution: int = 0,
        dataset: Dataset = None,
        plot_colors: dict = None,
        **kwargs,
    ) -> None:
        super().__init__(
            parent=parent,
            resolution=resolution,
            dataset=dataset,
            threadpool=threadpool,
            **kwargs,
        )

        self.width = 120
        self.image_resolution = resolution
        self.depth = dataset.meter_end()

        self.plot_colors = plot_colors

        self.image_frame = QWidget(self)
        self.image_frame.setToolTip(self.composite_tooltip(self.plot_colors))
        self.image_frame_layout = QVBoxLayout(self.image_frame)

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

    def _load_core_images(self) -> tuple:
        pixmaps = []
        pixmap_width = 0

        self.meter = self.dataset.get_row_meter()

        if self.meter.max() >= 9999:
            self.meter[:, 0] = np.arange(0, self.meter.shape[0], 1)
            self.meter[:, 1] = np.arange(1, self.meter.shape[0] + 1, 1)

        image_paths = {
            mineral: os_sorted(Path(self.dataset_info[mineral]).glob("*.png"))
            for mineral in self.data_name
        }
        total_image_height = 0
        for row_idx in range(self.dataset.n_rows()):
            row_image = np.array([0])
            n_ims = 0
            for min_idx, mineral in enumerate(self.data_name):
                image = Image.open(image_paths[mineral][row_idx])
                image_array = np.asarray(image) / 255
                if image_array.shape[2] > 3:
                    image_array = image_array[:, :, :3]
                min_color = self.hex_to_rgb(
                    self.plot_colors.get(self.data_name[min_idx])[1:]
                )
                colored_image = min_color * image_array

                if np.any(colored_image):
                    row_image = row_image + colored_image
                    n_ims = n_ims + 1

            if n_ims > 0:
                result = Image.fromarray(
                    (row_image / n_ims).astype(np.uint8), "RGB"
                )
            else:
                result = Image.fromarray(
                    (image_array * 0).astype(np.uint8), "RGB"
                )
            pixmap = QPixmap(ImageQt.ImageQt(result))
            pixmap_height = np.ceil(
                (self.meter[row_idx][1] - self.meter[row_idx][0])
                * self.resolution
            )
            pixmap = pixmap.scaledToHeight(pixmap_height)
            total_image_height = total_image_height + pixmap.height()
            if pixmap.width() > pixmap_width:
                pixmap_width = pixmap.width()

            pixmaps.append(pixmap)

        return pixmaps, pixmap_width, total_image_height

    def _display_core_images(self, result: tuple) -> None:
        pixmaps, pixmap_width, total_image_height = result

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
        self.clear_image_tiles()
        self.resolution = resolution
        self.get_images()
