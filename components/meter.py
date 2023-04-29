import numpy as np
from PySide6.QtCore import QPoint, Slot
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpacerItem


class Meter(QWidget):
    def __init__(
        self,
        parent=None,
        resolution: int = 0,
        height: int = 669,
        depth: int | float = 100,
    ) -> None:
        super().__init__(parent=parent)

        self.resolution = resolution
        self.height = height
        self.depth = depth

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addStretch()
        self.layout.addSpacing(17)
        self.setLayout(self.layout)

    def add_meter_tiles(self) -> None:
        self._clear_meter()

        tile_pixmaps = self._draw_meter_pixmaps()

        for pixmap in tile_pixmaps:
            tile = QLabel(self)
            tile.setPixmap(pixmap)
            self.insert_tile(tile)

    @Slot(int)
    def zoom_changed(self, resolution: int) -> None:
        self.resolution = resolution
        self.add_meter_tiles()

    @Slot(float, float)
    def update_size(self, new_max: int | float, new_height: int) -> None:
        if self.depth == new_max and self.height == new_height:
            return
        self.height = new_height
        self.depth = new_max
        self.add_meter_tiles()

    def insert_tile(self, tile: QLabel) -> None:
        if self.layout.count() == 1:
            self.layout.addWidget(tile)
            self.layout.addStretch()
        else:
            self.layout.insertWidget(self.layout.count() - 2, tile)

    def _clear_meter(self):
        for i in reversed(range(self.layout.count() - 1)):
            item = self.layout.itemAt(i)
            if not isinstance(item, QSpacerItem):
                item.widget().setVisible(False)
                item.widget().deleteLater()

    def _draw_meter_pixmaps(self) -> list:
        tile_height = 500  # height of tile in pixels
        total_height = self.depth * self.resolution

        if self.height > total_height:
            total_height = self.height

        total_height = np.floor(total_height / 25) * 25
        max_tick = total_height / self.resolution - 1

        # determine number of pixmaps needed for meterPos
        n_tiles = int(np.ceil(total_height / tile_height))
        stub_height = None  # length of last tile if shorter than others
        if total_height % tile_height != 0:
            stub_height = total_height % tile_height

        tick_values = np.arange(0, max_tick + 1, 10)
        tick_pos = [int(value * self.resolution) for value in tick_values]
        ticks = dict(zip(tick_pos, tick_values))

        pixmaps = []
        for n in range(n_tiles):
            if stub_height and n == n_tiles - 1:
                pm_height = stub_height
            else:
                pm_height = tile_height

            start_px = n * tile_height
            end_px = start_px + pm_height
            tile_ticks = [
                t for t in ticks.items() if t[0] >= start_px and t[0] <= end_px
            ]

            pixmap = QPixmap(60, pm_height)

            qp = QPainter(pixmap)  # initiate painter
            qp.setBrush(QColor(0, 0, 0))  # paint meter background black
            qp.drawRect(0, 0, 60, pm_height)
            qp.setBrush(QColor(222, 222, 222))  # set color for ticks and text
            qp.setPen(QColor(222, 222, 222))

            for tick in tile_ticks:
                tick_pos = tick[0] - n * tile_height
                qp.drawRect(15, tick_pos, 45, 1)
                qp.drawText(
                    QPoint(2, tick_pos + 17), "{:.1f}".format(tick[1]) + " m"
                )

            pixmaps.append(pixmap)

        return pixmaps
