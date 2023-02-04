import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.ticker import NullFormatter
from PySide6.QtCore import Slot

from components.data_panel import DataPanel


class SpectralPlotPanel(DataPanel):
    def __init__(self, parent=None, resolution: int = 0, **kwargs) -> None:
        super().__init__(parent=parent, resolution=resolution, **kwargs)

        self.width = 120
        self.image_resolution = resolution

        self.meta_data = self.config.data(
            self.dataset, self.datatype, self.datasubtype, self.dataname
        )

        self.setToolTip(f"{self.dataset} {self.dataname}")

        self._load_spectral_data()
        self._plot_spectral_data()

    def _load_spectral_data(self) -> None:

        csv_path = self.config.dataset(self.dataset).get("csv_path")

        data = np.genfromtxt(
            csv_path,
            delimiter=",",
            dtype="float",
            comments=None,
            skip_header=5,
            usecols=[
                self.meta_data.get("meter_from"),
                self.meta_data.get("meter_to"),
                self.meta_data.get("column"),
            ],
        )

        self.meter = (data[:, 0] + data[:, 1]) / 2
        self.meter_start = data[0, 0]
        self.meter_end = data[-1, 1]
        self.spectral_data = data[:, 2]

    def _plot_spectral_data(self) -> None:
        # create plot figure and canvas
        height = (self.meter_end - self.meter_start) * self.resolution
        plotFig = Figure(
            figsize=(self.width / 100, height / 100),
            dpi=100,
            facecolor="#000000",
        )
        plotCanvas = FigureCanvasQTAgg(plotFig)
        plotCanvas.draw()
        plotCanvas.setMouseTracking(True)

        # # make plot tooltip to display cursor coordinates and plot info
        # plotCanvas.mouseMoveEvent = lambda event: self.makePlotToolTip(
        #     event,
        #     newDataWindow,
        #     0,
        #     xMax,
        #     plotDepth[0],
        #     plotDepth[-1],
        #     unit,
        #     "spec",
        #     " ",
        # )

        xMin = float(self.meta_data.get("min_value"))
        xMax = float(self.meta_data.get("min_value"))

        plotFig.clear()
        plot = plotFig.add_axes([0, 0, 1, 1])
        plot.fill_betweenx(
            self.meter, xMin, self.spectral_data, facecolor="#ffffff"
        )
        # plot.set_yticks(meterVals)
        plot.set_xticks([xMin, (xMax + xMin) / 2, xMax])
        plot.set_ylim(self.meter_end, self.meter_start)
        plot.set_xlim([xMin, xMax])
        plot.set_frame_on(False)
        plot.grid(color="#323232")
        plot.xaxis.set_major_formatter(NullFormatter())
        plot.yaxis.set_major_formatter(NullFormatter())
        plotCanvas.draw()

        self.layout.addWidget(plotCanvas)

    @Slot(int)
    def zoom_changed(self, resolution: int) -> None:
        self.resolution = resolution
        self.layout.itemAt(0).widget().deleteLater()
        self._plot_spectral_data()
