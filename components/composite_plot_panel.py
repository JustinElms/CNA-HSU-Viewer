from pathlib import Path

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.ticker import NullFormatter
from PySide6.QtCore import Slot

from components.data_panel import DataPanel
from data.dataset import Dataset

"""
TODO
-resize plot instead of replotting it?
-add offset at top of panel
"""

TEMP_COLORS = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]


class CompositePlotPanel(DataPanel):
    def __init__(
        self,
        parent=None,
        resolution: int = 0,
        dataset: Dataset = None,
        **kwargs,
    ) -> None:
        super().__init__(
            parent=parent, resolution=resolution, dataset=dataset, **kwargs
        )

        self.width = 180
        self.setFixedWidth(self.width)
        self.image_resolution = resolution
        self.depth = dataset.meter_end()

        self.setToolTip(self.composite_tooltip())

        self._load_spectral_data()
        self._plot_spectral_data()

    def _load_spectral_data(self) -> None:
        mineral_columns = [min["column"] for min in self.dataset_info.values()]
        meter_from_column = self.dataset_info[self.data_name[0]]["meter_from"]
        meter_to_column = self.dataset_info[self.data_name[0]]["meter_to"]

        data = np.genfromtxt(
            Path(self.csv_data["path"]),
            delimiter=",",
            dtype="float",
            comments=None,
            skip_header=5,
            usecols=[
                meter_from_column,
                meter_to_column,
                *mineral_columns,
            ],
        )

        if data[-1, 1] >= 9999:
            data[:, 0] = np.arange(0, data.shape[0], 1)
            data[:, 1] = np.arange(1, data.shape[0] + 1, 1)

        self.bar_widths = data[:, 1] - data[:, 0]
        self.bar_centers = (data[:, 0] + data[:, 1]) / 2
        self.meter_start = data[0, 0]
        self.meter_end = data[-1, 1]
        self.spectral_data = data[:, 2:]

    def _plot_spectral_data(self) -> None:
        # create plot figure and canvas
        height = (self.meter_end - self.meter_start) * self.resolution
        plot_fig = Figure(
            figsize=(self.width / 100, height / 100),
            dpi=100,
            facecolor="#000000",
        )
        plotCanvas = FigureCanvasQTAgg(plot_fig)
        plotCanvas.draw()
        plotCanvas.setMouseTracking(True)

        # # make plot tooltip to display cursor coordinates and plot info
        # plotCanvas.mouseMoveEvent = lambda event: self.makePlotToolTip(
        #     event,
        #     newDataWindow,
        #     0,
        #     axis_max,
        #     plotDepth[0],
        #     plotDepth[-1],
        #     unit,
        #     "spec",
        #     " ",
        # )

        axis_min = 0.0
        axis_max = 1.0

        plot_fig.clear()
        plot = plot_fig.add_axes([0, 0, 1, 1])
        left = np.zeros(self.spectral_data.shape[0])
        for idx, spec in enumerate(self.spectral_data.transpose()):
            plot.barh(
                self.bar_centers,
                spec,
                self.bar_widths,
                left=left,
                facecolor=TEMP_COLORS[idx],
            )
            left = left + spec
        plot.set_xticks([axis_min, (axis_max + axis_min) / 2, axis_max])
        plot.set_ylim(self.meter_end, self.meter_start)
        plot.set_xlim(axis_min, axis_max)
        plot.set_frame_on(False)
        plot.grid(color="#323232")
        plot.xaxis.set_major_formatter(NullFormatter())
        plot.yaxis.set_major_formatter(NullFormatter())
        plotCanvas.draw()

        self.insert_plot(plotCanvas)

    @Slot(int)
    def zoom_changed(self, resolution: int) -> None:
        self.resolution = resolution
        self.layout.itemAt(0).widget().deleteLater()
        self._plot_spectral_data()

    def insert_plot(self, plot: FigureCanvasQTAgg) -> None:
        if self.layout.count() == 0:
            self.layout.addWidget(plot)
            self.layout.addStretch()
        else:
            self.layout.insertWidget(self.layout.count() - 1, plot)

    def composite_tooltip(self) -> str:
        tag = ""
        for idx, mineral in enumerate(self.data_name):
            tag = (
                tag
                + '<font color="'
                + TEMP_COLORS[idx]
                + '">■</font> '
                + mineral
            )
            if idx != len(self.data_name) - 1:
                tag = tag + "<br>"
        return tag
