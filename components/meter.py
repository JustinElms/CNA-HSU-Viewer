from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from plotters.meter import draw_meter_tiles


class Meter(QWidget):
    def __init__(
        self, parent=None, resolution: int = 0, depth: int | float = 100
    ) -> None:
        super().__init__(parent=parent)

        self.resolution = resolution
        self.depth = depth

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addStretch()
        self.setLayout(self.layout)

        self.setStyleSheet("background-color: red;")

        self._plot()

    def _plot(self) -> None:

        tiles = draw_meter_tiles(self.resolution, self.depth)

        for tile in tiles:
            label = QLabel(self)
            label.setPixmap(tile)
            self.insert_tile(label)

    @Slot(int)
    def zoom_changed(self, resolution: int) -> None:
        self.resolution = resolution
        for i in reversed(range(self.layout.count() - 1)):
            self.layout.itemAt(i).widget().deleteLater()

        self._plot()

    @Slot(int)
    def update_size(self, height: float) -> None:
        print("meter geom")
        print(self.geometry())

        self.depth = self.resolution * height
        for i in reversed(range(self.layout.count() - 1)):
            self.layout.itemAt(i).widget().deleteLater()
        # self._plot()

    def insert_tile(self, tile: QLabel) -> None:
        if self.layout.count() == 0:
            self.layout.addWidget(tile)
            self.layout.addStretch()
        else:
            self.layout.insertWidget(self.layout.count() - 1, tile)
