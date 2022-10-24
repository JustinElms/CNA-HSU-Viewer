from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)


from drawing import *


class DataWidget(QWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__()

        self.kwargs = kwargs

        self.width = self.kwargs["width"]
        self.height = self.kwargs["height"]

        self.setFixedSize(self.width, self.height)

        # configure widget layout
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 20, 0, 0)

        self.widget_type = self.kwargs["widget_type"]

        if self.widget_type == "core_images":
            title = self.kwargs["title"]
            axis_limit_label = ["", ""]
        elif self.widget_type == "spec_plot":
            title = self.kwargs["title"]
            axis_limit_label = self.kwargs["axis_limits"]
            if self.kwargs["unit"] == "%":
                axis_limit_label = [str(x * 100) for x in axis_limit_label]
        elif self.widget_type == "stack_plot":
            title = " "
            axis_limit_label = ["0", "100"]
            self.minColorChanged = []

        self.make_body(title)
        self.make_header(title, axis_limit_label)

    def make_header(self, title, axis_limits):

        # create container widget for header
        self.header = QWidget(self)
        self.header.setFixedHeight(40)
        self.header.setStyleSheet("Background-Color: transparent")
        headerLayout = QVBoxLayout(self.header)
        headerLayout.setSpacing(0)
        headerLayout.setContentsMargins(0, 0, 0, 0)

        # container for header title
        titleArea = QWidget(self.header)
        titleArea.setFixedHeight(20)
        titleArea.setStyleSheet("Background-Color: rgba(100,100,100,150)")
        titleAreaLayout = QHBoxLayout(titleArea)
        titleAreaLayout.setSpacing(0)
        titleAreaLayout.setContentsMargins(0, 0, 0, 0)

        # label for header title
        titleLabel = QLabel(titleArea)
        titleLabel.setFixedHeight(20)
        titleLabel.setText(title)
        titleLabel.setStyleSheet(
            "background-color: transparent; font: bold 10pt; border: transparent"
        )

        self.closeButton = QPushButton(titleArea)
        self.closeButton.setText("X")
        self.closeButton.setFixedSize(20, 20)
        self.closeButton.setStyleSheet(
            "background-color: transparent; font: bold 10pt; border: transparent"
        )

        titleAreaLayout.addStretch()
        titleAreaLayout.addWidget(titleLabel)
        titleAreaLayout.addStretch()
        titleAreaLayout.addWidget(self.closeButton)

        # area for axis limits
        axisLabelArea = QWidget(self.header)
        axisLabelArea.setFixedHeight(20)
        axisLabelAreaLayout = QHBoxLayout(axisLabelArea)
        axisLabelAreaLayout.setSpacing(0)
        axisLabelAreaLayout.setContentsMargins(0, 0, 0, 0)

        # label for axis minimum
        axisStartLabel = QLabel(axisLabelArea)
        axisStartLabel.setFixedHeight(20)
        axisStartLabel.setStyleSheet(
            "background-color: transparent; font: bold 10pt; border: transparent"
        )
        axisStartLabel.setText(str(axis_limits[0]))

        # label for axis maximum
        axisEndLabel = QLabel(axisLabelArea)
        axisEndLabel.setFixedHeight(20)
        axisEndLabel.setStyleSheet(
            "background-color: transparent; font: bold 10pt; border: transparent"
        )
        axisEndLabel.setText(str(axis_limits[1]))

        axisLabelAreaLayout.addWidget(axisStartLabel)
        axisLabelAreaLayout.addStretch()
        axisLabelAreaLayout.addWidget(axisEndLabel)

        headerLayout.addWidget(titleArea)
        headerLayout.addWidget(axisLabelArea)
        headerLayout.addStretch()

        self.header.setGeometry(0, 0, self.width, self.height)
        self.header.raise_()

    def make_body(self, title):

        # create container widget for body
        self.body = QWidget(self)
        self.bodyLayout = QVBoxLayout(self.body)
        self.bodyLayout.setSpacing(0)
        self.bodyLayout.setContentsMargins(0, 0, 0, 0)

        if self.widget_type == "core_images":
            self.addCoreIms(title)
        elif self.widget_type == "spec_plot":
            self.addSpecPlot(self.kwargs["color"])
        elif self.widget_type == "stack_plot":
            self.addStackPlot(self.kwargs["color"])

        self.layout.addWidget(self.body)

    def update_size(self, width, height):
        self.width = width
        self.height = height
        self.setFixedSize(width, height)
        self.header.setFixedSize(width, 40)

    def move_header(self, value):
        self.header.setGeometry(0, value, self.width, self.height)

    def makePlotToolTip(
        self, event, parent, minX, maxX, minY, maxY, unit, plotType, legend
    ):
        """
        displays depth and plot values in tooltip, takes axis ranges, plot units, type,
         and the legend to display
        """

        # checks to see that mouse is over plot and adds data to tooltip
        if event.y() > 20 and event.y() < self.height:
            yPos = minY + (event.y() - 20) * (maxY - minY) / (self.height)
            xPos = minX + (event.x()) * (maxX - minX) / (self.width)

            if plotType == "spec":
                parent.setToolTip(
                    "{:.1f}".format(yPos) + " m, " + "{:.1f}".format(xPos) + " " + unit
                )
            elif plotType == "stack":
                parent.setToolTip(
                    "{:.1f}".format(yPos)
                    + " m, "
                    + "{:.1f}".format(xPos)
                    + " "
                    + unit
                    + "<br>"
                    + legend
                )

    def addCoreIms(self, title):
        ims = self.kwargs["images"]
        content = drawCoreImages(self.body, title, ims)
        self.bodyLayout.addWidget(content)

    def addSpecPlot(self, color):
        if self.bodyLayout is not None:
            while self.bodyLayout.count():
                item = self.bodyLayout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        data = self.kwargs["data"]
        axis_limits = self.kwargs["axis_limits"]
        depth = self.kwargs["depth"]
        meter_values = self.kwargs["meter_values"]
        unit = self.kwargs["unit"]
        content = drawSpecPlot(
            self.width, self.height, data, axis_limits, depth, color, meter_values
        )
        content.mouseMoveEvent = lambda event: self.makePlotToolTip(
            event,
            content,
            axis_limits[0],
            axis_limits[1],
            depth[0],
            depth[-1],
            unit,
            "spec",
            " ",
        )

        self.bodyLayout.addWidget(content)

    def addStackPlot(self, color):
        if self.bodyLayout is not None:
            while self.bodyLayout.count():
                item = self.bodyLayout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        data = self.kwargs["data"]
        dimensions = self.kwargs["dimensions"]
        min_names = self.kwargs["min_names"]
        depth = self.kwargs["depth"]
        meter_values = self.kwargs["meter_values"]

        plotColor = [color[mineral] for mineral in min_names]

        # create a legend for the toolTip
        tag = " "
        for i in range(len(min_names)):
            tag = tag + '<font color="' + plotColor[i] + '">■</font> ' + min_names[i]
            if i != len(min_names) - 1:
                tag = tag + "<br>"

        content = drawStackPlot(
            self.width, self.height, data, dimensions, plotColor, depth, meter_values
        )
        content.mouseMoveEvent = lambda event: self.makePlotToolTip(
            event, content, 0, 100, depth[0], depth[-1], "%", "stack", tag
        )

        self.bodyLayout.addWidget(content)
