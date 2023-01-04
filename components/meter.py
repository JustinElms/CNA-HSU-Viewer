from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from plotters.meter import draw_meter_tiles

# resolution of each zoom level, zoom level: m/10px
METER_RES_LEVELS = {
    0: 20,
    1: 40,
    2: 60,
    3: 80,
    4: 100,
}


class Meter(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)

        self.zoom_level = 1

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self._plot(self.zoom_level)

    def _plot(self, zoom_level: int, max_depth: int = 500) -> None:

        tiles = draw_meter_tiles(zoom_level, max_depth)

        for tile in tiles:
            label = QLabel(self)
            label.setPixmap(tile)
            self.layout.addWidget(label)

        self.layout.addStretch()
