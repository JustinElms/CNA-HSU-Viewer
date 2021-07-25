from PySide2.QtCore import QPoint, Qt, Signal
from PySide2.QtGui import QIcon, QMouseEvent
from PySide2.QtWidgets import (QButtonGroup, QCheckBox,
                               QComboBox, QFileDialog, QFrame, QGridLayout,
                               QGroupBox, QHBoxLayout, QLabel, QMainWindow,
                               QPushButton, QScrollArea, QSizePolicy, QSlider,
                               QVBoxLayout, QWidget)


from drawing import *


class DataWidget(QWidget):

    def __init__(self, parent=None, **kwargs):
        super().__init__()

        self.width = kwargs["width"]
        self.height = kwargs["height"]

        self.setFixedSize(self.width,self.height)

        # configure widget layout
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,20,0,0)

        self.widget_type = kwargs["widget_type"]
        
        if self.widget_type == 'core_images':
            title = kwargs["title"]
            axis_limit_label = ['','']
        elif self.widget_type == 'spec_plot':
            title = kwargs["title"]
            axis_limit_label = kwargs['axis_limits']
            if kwargs['unit'] == '%':
                axis_limit_label = [str(x*100) for x in axis_limit_label] 
            #self.color_changed = kwargs["color_signal"]
        elif self.widget_type == 'stack_plot':
            title = " "
            axis_limit_label = ["0", "100"]

        self.make_body(title, kwargs)
        self.make_header(title, axis_limit_label)
    
    def make_header(self, title, axis_limits):

        # create container widget for header
        self.header = QWidget(self)
        self.header.setFixedHeight(40)  
        self.header.setStyleSheet('Background-Color: transparent')
        headerLayout = QVBoxLayout(self.header)
        headerLayout.setSpacing(0)
        headerLayout.setContentsMargins(0,0,0,0)

        # container for header title
        titleArea = QWidget(self.header)
        titleArea.setFixedHeight(20)
        titleArea.setStyleSheet('Background-Color: rgba(100,100,100,150)')
        titleAreaLayout = QHBoxLayout(titleArea)
        titleAreaLayout.setSpacing(0)
        titleAreaLayout.setContentsMargins(0,0,0,0)

        # label for header title
        titleLabel = QLabel(titleArea)
        titleLabel.setFixedHeight(20)
        titleLabel.setText(title)
        titleLabel.setStyleSheet('background-color: transparent; font: bold 10pt; border: transparent')

        self.closeButton = QPushButton(titleArea)
        self.closeButton.setText('X')
        self.closeButton.setFixedSize(20,20)
        self.closeButton.setStyleSheet('background-color: transparent; font: bold 10pt; border: transparent')

        titleAreaLayout.addStretch()
        titleAreaLayout.addWidget(titleLabel)
        titleAreaLayout.addStretch()
        titleAreaLayout.addWidget(self.closeButton)

        # area for axis limits
        axisLabelArea = QWidget(self.header)
        axisLabelArea.setFixedHeight(20)
        axisLabelAreaLayout = QHBoxLayout(axisLabelArea)
        axisLabelAreaLayout.setSpacing(0)
        axisLabelAreaLayout.setContentsMargins(0,0,0,0)

        # label for axis minimum
        axisStartLabel = QLabel(axisLabelArea)
        axisStartLabel.setFixedHeight(20)
        axisStartLabel.setStyleSheet('background-color: transparent; font: bold 10pt; border: transparent')
        axisStartLabel.setText(str(axis_limits[0]))

        # label for axis maximum
        axisEndLabel = QLabel(axisLabelArea)
        axisEndLabel.setFixedHeight(20)
        axisEndLabel.setStyleSheet('background-color: transparent; font: bold 10pt; border: transparent')
        axisEndLabel.setText(str(axis_limits[1]))

        axisLabelAreaLayout.addWidget(axisStartLabel)
        axisLabelAreaLayout.addStretch()
        axisLabelAreaLayout.addWidget(axisEndLabel)        

        headerLayout.addWidget(titleArea)
        headerLayout.addWidget(axisLabelArea)
        headerLayout.addStretch()

        self.header.setGeometry(0,0,self.width,self.height)
        self.header.raise_()
        
    def make_body(self, title, args):
        
        # create container widget for body
        body = QWidget(self)
        bodyLayout = QVBoxLayout(body)
        bodyLayout.setSpacing(0)
        bodyLayout.setContentsMargins(0,0,0,0)

        if self.widget_type == 'core_images':
            ims = args["images"]
            content = drawCoreImages(body, bodyLayout, title, ims)
        elif self.widget_type == 'spec_plot':
            data = args["data"]
            axis_limits = args["axis_limits"]
            depth = args["depth"] 
            color = args["color"] 
            meter_values = args["meter_values"] 
            unit = args["unit"]  
            content = drawSpecPlot(self.width, self.height, data, axis_limits, depth, color, meter_values)
            content.mouseMoveEvent = lambda event: self.makePlotToolTip(event, content, axis_limits[0], axis_limits[1], depth[0], depth[-1], unit, 'spec', ' ')

        elif self.widget_type == 'stack_plot':
            data = args["data"]
            dimensions = args["dimensions"]
            color = args["color"]
            min_names = args["min_names"]
            depth = args["depth"]
            meter_values = args["meter_values"]

            # create a legend for the toolTip
            tag = ' '
            for i in range(len(min_names)):
                tag = tag  + '<font color="' + color[i] + '">■</font> ' + min_names[i]
                if i != len(min_names)-1:
                    tag = tag + '<br>'
            
            content = drawStackPlot(self.width, self.height, data, dimensions, color, depth, meter_values)
            content.mouseMoveEvent = lambda event: self.makePlotToolTip(event, content, 0, 100, depth[0], depth[-1], '%', 'stack', tag)

        #self.minColorChanged.connect(lambda: drawSpecPlot(plotFig, plotCanvas, plotSpec, xMin, xMax, plotDepth, self.plotColorDict[mineral], self.meterVals))
        
        bodyLayout.addWidget(content)
        self.layout.addWidget(body)
        
    def update_size(self, width, height):
        self.width = width
        self.height = height
        self.setFixedSize(width,height)
        self.header.setFixedSize(width, 40)

    def move_header(self, value):
        self.header.setGeometry(0,value,self.width,self.height)

    def makePlotToolTip(self, event, parent, minX, maxX, minY, maxY, unit, plotType, legend):
        """
         displays depth and plot values in tooltip, takes axis ranges, plot units, type,
          and the legend to display
        """

        # checks to see that mouse is over plot and adds data to tooltip
        if event.y() > 20 and event.y()<self.height: 
            yPos = minY + (event.y()-20)*(maxY-minY)/(self.height)
            xPos = minX + (event.x())*(maxX-minX)/(self.width)

            if plotType == 'spec':
                parent.setToolTip("{:.1f}".format(yPos) + ' m, ' + "{:.1f}".format(xPos) + ' ' + unit )
            elif plotType == 'stack':
                parent.setToolTip("{:.1f}".format(yPos) + ' m, ' + "{:.1f}".format(xPos) + ' ' + unit + '<br>' + legend)



