from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from plotters.meter import draw_meter_tiles


class Meter(QWidget):
    def __init__(
        self,
        parent=None,
        resolution: int = 0,
        min_depth: int | float = 0,
        max_depth: int | float = 100,
    ) -> None:
        super().__init__(parent=parent)

        self.resolution = resolution
        self.min_depth = min_depth
        self.max_depth = max_depth

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def _plot(self) -> None:

        # if self.max_depth - self.min_depth >0:
        tiles = draw_meter_tiles(self.resolution, self.max_depth)

        for tile in tiles:
            label = QLabel(self)
            label.setPixmap(tile)
            self.insert_tile(label)

    @Slot(int)
    def zoom_changed(self, resolution: int) -> None:
        self.resolution = resolution
        self._clear_meter()
        self._plot()

    @Slot(float, float)
    def update_size(self, new_min: int | float, new_max: int | float) -> None:
        if self.min_depth == new_min and self.max_depth == new_max:
            return
        self.min_depth = new_min
        self.max_depth = new_max
        self._clear_meter()
        self._plot()

    def insert_tile(self, tile: QLabel) -> None:
        if self.layout.count() == 0:
            self.layout.addWidget(tile)
            self.layout.addStretch()
        else:
            self.layout.insertWidget(self.layout.count() - 1, tile)

    def _clear_meter(self):
        for i in reversed(range(self.layout.count() - 1)):
            self.layout.itemAt(i).widget().deleteLater()
