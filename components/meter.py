from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from plotters.meter import draw_meter_tiles


class Meter(QWidget):
    def __init__(self, parent=None, zoom_level: int = 0) -> None:
        super().__init__(parent=parent)

        self.zoom_level = zoom_level

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self._plot()

    def _plot(self, max_depth: int = 100) -> None:

        tiles = draw_meter_tiles(self.zoom_level, max_depth)

        for tile in tiles:
            label = QLabel(self)
            label.setPixmap(tile)
            self.layout.addWidget(label)

        self.layout.addStretch()
