import numpy as np
from matplotlib.ticker import NullFormatter
from PySide2.QtCore import Qt, QPoint
from PySide2.QtGui import QColor, QPainter, QPixmap
from PySide2.QtWidgets import QFrame, QGridLayout, QLabel, QSizePolicy


def drawMeter(depthValues, width, height):
        """
         draws pixmaps for down-hole meter. Maximum pixmap size is 32767 px so multiple pixmaps
         may be needed depending on depth of drill hole and image sizes
        """
        
        # determine number of pixmaps needed for meterPos
        numPixmaps = np.ceil(height/32767).astype(int)

        # create list of pixmaps for meter
        pixmap = []
        if numPixmaps == 1:
            pixmap.append(QPixmap(width, height))
        else:
            for i in range(numPixmaps):
                if i == (numPixmaps - 1):
                    pxHeight = height% (i *32767)
                else:
                    pxHeight = 32767
                pixmap.append(QPixmap(width, pxHeight))

        # determine space between meter ticks
        tickSpace = np.ceil(height/len(depthValues))
        pxNum = 0

        # check that height of pixmap is less than 32767
        if height > 32767:
            pxHeight = 32767
        else:
            pxHeight = height

        qp = QPainter(pixmap[pxNum])                            # initiate painter
        qp.setBrush(QColor(0, 0, 0))                            # paint meter background black
        qp.drawRect(0, 0, width, pxHeight)
        qp.setBrush(QColor(222, 222, 222))                      # set color for ticks and text
        qp.setPen(QColor(222,222,222))

        # # draw meter pixmaps
        for i in range(len(depthValues)):
            if i*tickSpace > (pxNum+1)*32767:
                pxNum = pxNum + 1
                if pxNum == (numPixmaps - 1):
                    pxHeight = height% (pxNum *32767)
                else:
                    pxHeight = 32767

                qp = QPainter(pixmap[pxNum])
                qp.setBrush(QColor(0, 0, 0))
                qp.drawRect(0, 0, width, pxHeight)
                qp.setBrush(QColor(222, 222, 222))
                qp.setPen(QColor(222,222,222))

            if i == 0 and pxNum == 0:                                   # starting major tick and text
                qp.drawRect(int(0.25*width), 20, int(0.75*width), 1)
                qp.drawText(QPoint(0, 17), "{:.1f}".format(depthValues[i]) + ' m')
             #elif i%numCoresPerBox == 0:                                            # other major ticks and text
            else:
                qp.drawRect(int(0.25*width), i*tickSpace+20-pxNum*32767, int(0.75*width), 1)
                qp.drawText(QPoint(0, i*tickSpace-pxNum*32767+17), "{:.1f}".format(depthValues[i]) + ' m')

        return pixmap

def drawCoreImages(parent, parentLayout, title, ims):
    """
        draws coreImages on dataWidget
    """
    
    # frame for core images
    coreFrame = QFrame(parent)
    coreFrameLayout = QGridLayout(coreFrame)

    # create labels for each core image and add to coreFrame
    for i in range(len(ims)):
        coreIm = QLabel(coreFrame)
        coreIm.setScaledContents(True)
        pixmap = ims[i]
        coreIm.setPixmap(pixmap)
        coreFrameLayout.addWidget(coreIm,i,1)

    coreFrameLayout.setSpacing(0)
    coreFrameLayout.setContentsMargins(0,0,0,0)
    coreFrame.setToolTip(title)         # tooltip displays min name when hovering mouse over widget

    parentLayout.addWidget(coreFrame)

def drawSpecPlot(plotFig, plotCanvas, plotSpec, xMin, xMax, plotDepth, plotColor, meterVals):
    """
    draws plot used in addSpectralPlotWindow. takes reference to plotFig and plotCanvas,
    plot and depth data, and the plot's color
    """

    plotFig.clear()
    plot = plotFig.add_axes([0,0,1,1])
    plot.fill_betweenx(plotDepth, xMin, plotSpec, facecolor=plotColor)
    plot.set_yticks(meterVals)
    plot.set_xticks([xMin, (xMax+xMin)/2, xMax])
    plot.set_ylim(float(plotDepth[-1]), float(plotDepth[0]))
    plot.set_xlim([xMin, xMax])
    plot.set_frame_on(False)
    plot.grid(color='#323232')
    plot.xaxis.set_major_formatter(NullFormatter())
    plot.yaxis.set_major_formatter(NullFormatter())
    plotCanvas.draw()

def drawStackPlot(plotFig, plotCanvas, plotSpec, specDim, plotColor, plotMinNames, minMeter, meterVals):
    """
    draws plot used in addStackPlotWindow. takes reference to plotFig and plotCanvas,
    plot and depth data
    """

    # clear the figure incase plot needs to be redrawn and set new axis limits
    plotFig.clear()
    plot = plotFig.add_axes([0,0,1,1])
    plot.set_ylim(float(minMeter[-1]), float(minMeter[0]))

    # plot each column of plotSpec and fill between them
    for i in range(specDim[1] + 1):
        if i==0:
            plot.fill_betweenx(minMeter,plotSpec[:,i], facecolor = plotColor[i])
        elif i > 0 and i < specDim[1]:
            plot.fill_betweenx(minMeter,plotSpec[:,i],plotSpec[:,i-1], facecolor = plotColor[i])
        else:
            plot.fill_betweenx(minMeter,plotSpec[:,i],plotSpec[:,i-1], facecolor ='#969696')

    # set ticks at 0, 50, adn 100% and draw plot
    plot.set_yticks(meterVals)
    plot.set_xticks([0, 0.5, 1])
    plot.set_ylim(float(meterVals[-1]), float(meterVals[0]))
    plot.set_xlim([0, 1])
    plot.set_frame_on(False)
    plot.grid(color='#323232')
    plot.xaxis.set_major_formatter(NullFormatter())
    plot.yaxis.set_major_formatter(NullFormatter())
    plotCanvas.draw()

