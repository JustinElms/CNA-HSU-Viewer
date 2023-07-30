from pathlib import Path

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.ticker import NullFormatter
from PySide6.QtCore import Signal, Slot

from components.data_panel import DataPanel
from data.dataset import Dataset
from hsu_viewer.worker import Worker

"""
TODO
-resize plot instead of replotting it?
-add offset at top of panel
"""


class CompositePlotPanel(DataPanel):
    update_axis_limits = Signal(list)

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

        self.width = 180
        self.setFixedWidth(self.width)
        self.image_resolution = resolution
        self.depth = dataset.meter_end()

        self.plot_colors = plot_colors

        self.axis_limits = [0, 1]

        self.setToolTip(self.composite_tooltip(self.plot_colors))

        self.loading.emit(True)
        self.get_plot()

    def get_plot(self) -> None:
        if self.threadpool:
            worker = Worker(self._load_spectral_data)
            worker.signals.result.connect(self._plot_spectral_data)
            worker.signals.finished.connect(self._on_finish)
            self.threadpool.start(worker)
        else:
            result = self._load_spectral_data()
            self._plot_spectral_data(result)
            self.loading.emit(False)

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

        if data[0, 0] != 0:
            top_row = np.full([1, data.shape[1]], np.nan)
            top_row[0, 0] = 0
            top_row[0, 1] = data[0, 0]
            data = np.insert(data.astype(float), 0, top_row, axis=0)

        bar_widths = data[:, 1] - data[:, 0]
        bar_centers = (data[:, 0] + data[:, 1]) / 2
        meter_start = data[0, 0]
        meter_end = data[-1, 1]
        spectral_data = data[:, 2:]

        return bar_widths, bar_centers, meter_start, meter_end, spectral_data

    def _plot_spectral_data(self, result: tuple) -> None:
        # create plot figure and canvas
        bar_widths, bar_centers, meter_start, meter_end, spectral_data = result

        if self.layout.count() > 0:
            self.layout.itemAt(0).widget().deleteLater()

        height = (meter_end - meter_start) * self.resolution
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

        plot_fig.clear()
        plot = plot_fig.add_axes([0, 0, 1, 1])
        left = np.zeros(spectral_data.shape[0])
        for idx, spec in enumerate(spectral_data.transpose()):
            plot_color = self.plot_colors.get(self.data_name[idx])
            plot.barh(
                bar_centers,
                spec,
                bar_widths,
                left=left,
                facecolor=plot_color,
            )
            left = left + spec
        axis_max = np.nanmax(left)
        self.update_axis_limits.emit([0, axis_max])
        plot.set_xticks([0, axis_max / 2, axis_max])
        plot.set_ylim(meter_end, meter_start)
        plot.set_xlim(0, axis_max)
        plot.set_frame_on(False)
        plot.grid(color="#323232")
        plot.xaxis.set_major_formatter(NullFormatter())
        plot.yaxis.set_major_formatter(NullFormatter())
        plotCanvas.draw()

        self.insert_plot(plotCanvas)

    @Slot(int)
    def zoom_changed(self, resolution: int) -> None:
        self.loading.emit(True)
        self.resolution = resolution
        self.get_plot()

    def insert_plot(self, plot: FigureCanvasQTAgg) -> None:
        if self.layout.count() == 0:
            self.layout.addWidget(plot)
            self.layout.addStretch()
        else:
            self.layout.insertWidget(self.layout.count() - 1, plot)
