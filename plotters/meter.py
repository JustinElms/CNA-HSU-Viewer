import numpy as np

# from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import NullFormatter
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel

# resolution of each zoom level, zoom level: m/100px
METER_RES_LEVELS = {
    1: 200,
    2: 160,
    3: 120,
    4: 80,
    5: 40,
}


def draw_meter_tiles(zoom_level: int, depth: int) -> QPixmap:
    """
    draws pixmaps for down-hole meter. Maximum pixmap size is 32767 px so multiple pixmaps
    may be needed depending on depth of drill hole and image sizes
    """

    tile_height = 500

    # determine number of pixmaps needed for meterPos
    res = METER_RES_LEVELS[zoom_level]  # m/100px
    px_height = np.ceil(res * depth / 100)

    n_tiles = int(np.ceil(px_height / tile_height))
    stub_height = None  # length of last tile if different
    if px_height % tile_height != 0:
        stub_height = px_height % tile_height + 10

    tick_values = np.arange(0, depth + 1, int(100 / zoom_level))
    n_ticks = tick_values.size
    tick_spacing = np.ceil(px_height / n_ticks)
    tick_pos = [int(n * tick_spacing) for n in range(n_ticks)]
    ticks = dict(zip(tick_pos, tick_values))

    tiles = []
    for n in range(n_tiles):
        if n_tiles == 1:
            pm_height = tile_height + 10
        elif stub_height and n == n_tiles:
            pm_height = stub_height
        elif n == n_tiles:
            pm_height = tile_height + 10
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
            qp.drawText(QPoint(2, tick_pos + 17), "{:.1f}".format(tick[1]) + " m")

        tiles.append(pixmap)

    return tiles
