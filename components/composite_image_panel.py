from pathlib import Path

import numpy as np
from natsort import os_sorted
from PIL import Image, ImageEnhance, ImageQt
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PySide6.QtGui import QColor, QPainter, QPixmap

from components.data_panel import DataPanel
from data.dataset import Dataset
from hsu_viewer.worker import Worker


class CompositeImagePanel(DataPanel):
    """Component for Composite Core Images

    Handles production, manipulation, and display of stacked (composite) core
    images.
    """

    def __init__(
        self,
        parent=None,
        threadpool=None,
        resolution: int = 0,
        dataset: Dataset = None,
        plot_colors: dict = None,
        **kwargs,
    ) -> None:
        """Initialize component

        Args:
            parent(None/QWidget): The parent widget.
            threadpool(None/QThreadpool): The threadpool used to handle async
                operations.
            resolution(int): The curently selected resolution (px/m)
            dataset(Dataset): The dataset object for the selected mineral data.
            plot_colors(dict): A dictionary of colors to be assigned to each
                mineral.
        """
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
        """Handles the process of loading and displying images in the widget.
        Can be run asynchronously if a theadpool was assigned.
        """
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
        """Loads each image to needed then stacks images from each row into a
        composite row.
        """
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
                comp_image = Image.fromarray(
                    (row_image / n_ims).astype(np.uint8), "RGB"
                )
            else:
                comp_image = Image.fromarray(
                    (image_array * 0).astype(np.uint8), "RGB"
                )
            enhancer = ImageEnhance.Brightness(comp_image)
            comp_image = enhancer.enhance(5)
            pixmap = QPixmap(ImageQt.ImageQt(comp_image))
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
        """Scales the images and adds them to the image_frame object.

        Args:
            result(tuple): A tuple containing image data and size parameters.

        """
        pixmaps, pixmap_width, total_image_height = result

        self.clear_image_tiles()

        for pixmap in pixmaps:
            image = QLabel()
            image.setScaledContents(True)
            image.setPixmap(pixmap)
            self.insert_row(image)

        self.image_frame_layout.setSpacing(0)
        self.image_frame_layout.setContentsMargins(0, 0, 0, 0)

        frame_height = (self.meter[-1][1] - self.meter[0][0]) * self.resolution
        frame_width = int(pixmap_width * frame_height / total_image_height)
        self.image_frame.setFixedSize(frame_width, frame_height)
        self.width = frame_width
        self.setFixedWidth(self.width)

    def insert_row(self, tile: QLabel) -> None:
        """Inserts each row image into the image_fram object.

        Args:
            tile(QLabel): A QLabel object containing the image to be displayed.

        """
        if self.image_frame_layout.count() == 0:
            self.image_frame_layout.addWidget(tile)
            self.image_frame_layout.addStretch()
        else:
            self.image_frame_layout.insertWidget(
                self.image_frame_layout.count() - 1, tile
            )

    @Slot(int)
    def zoom_changed(self, resolution: int) -> None:
        """Updates the image sizes when the resolution is changed.

        Args:
            resolution(int): The new resoltuion (px/m).

        """
        self.loading.emit(True)
        self.resolution = resolution
        self.get_images()
