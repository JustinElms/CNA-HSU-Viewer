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
    """Base class for all data panels.

    Signals:
        resize_header(int): Resizes a panel's header when its width chagnes.
        loading(bool): Triggers loading display during panel operations.
    """

    resize_header = Signal(int)
    loading = Signal(bool)

    def __init__(
        self,
        parent=None,
        threadpool=None,
        resolution: int = 0,
        dataset: Dataset = None,
        **kwargs
    ) -> None:
        """Initialize component

        Args:
            parent(None/QWidget): The parent widget.
            threadpool(None/QThreadpool): The threadpool used to handle async
                operations.
            resolution(int): The curently selected resolution (px/m)
            dataset(Dataset): The dataset object for the selected mineral data.
        """
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
        self.csv_data = self.dataset.config.get("csv_data")

        self.loading_panel = LoadingPanel(self)
        self.loading_panel.raise_()
        self.loading.connect(self.set_loading)

        self.setFixedWidth(120)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    @Slot()
    def close_panel(self) -> None:
        """Deletes the panel on close."""
        self.deleteLater()

    @Slot(bool)
    def set_loading(self, show_loading: bool) -> None:
        """Displays the loading image during data operations.

        Args:
            show_loading(bool): Whether or not to display the loading image.
        """
        self.loading_panel.raise_()
        if show_loading:
            self.loading_panel.show()
        else:
            self.loading_panel.hide()

    @Slot()
    def _on_finish(self) -> None:
        """Signals that loading has completed for async operations."""
        self.loading.emit(False)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handles resizing of panel when the application is
        resized or zoom is changed.

        Args:
            event (QResizeEvent): The QResizeEvent triggering this change.
        """
        self.resize_header.emit(self.geometry().width())

    def hex_to_rgb(self, hex):
        """Converts hex color codes to rgb

        Args:
            hex: hex color value.
        """
        return np.array([int(hex[i : i + 2], 16) for i in (0, 2, 4)])

    def composite_tooltip(self, plot_colors: dict) -> str:
        """Creates the legend tooltip for composit plots with one or more
        mineral.

        Args:
            plot_colors(dict): The assigned colors for each mineral.
        """
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
        """Removes all image tiles in a panel."""
        for i in reversed(range(self.image_frame_layout.count())):
            item = self.image_frame_layout.itemAt(i)
            if not isinstance(item, QSpacerItem):
                item.widget().setVisible(False)
                item.widget().deleteLater()

    def update_plot_colors(self, mineral: str, color: str) -> None:
        self.plot_colors[mineral] = color
        self.loading.emit(True)
        self.get_plot()
