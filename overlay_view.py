import numpy as np
import qimage2ndarray
from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import (QComboBox, QFrame, QGridLayout, QHBoxLayout,
                               QLabel, QPushButton, QSlider, QVBoxLayout,
                               QWidget)


class overlayView(QWidget):
    """
     The overlayView class creates a window which allows users to overlay spectral images
     onto core box images
    """
    def __init__(self, parent):
        super(overlayView, self).__init__(parent)
        """
         initializes widgets used in the overlayView class
        """

        # empty list to contain hex color values for overlay
        self.colors = []

        # main widget layout
        layout = QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        self.setStyleSheet('background-color: rgb(0,0,0)')

        # controlArea contains buttons and sliders used to control overlay behavior
        controlArea = QWidget(self)
        controlArea.setFixedWidth(250)
        controlAreaLayout = QVBoxLayout(controlArea)
        controlAreaLayout.setSpacing(0)
        controlAreaLayout.setContentsMargins(0,0,0,0)

        # buttonBar sits at the top of controlArea, used to select core boxes for overlay
        buttonBar = QFrame(controlArea)
        buttonBar.setFixedHeight(30)
        buttonBar.setStyleSheet('background-color: rgb(40,44,52)')
        buttonBarLayout = QHBoxLayout(buttonBar)
        buttonBarLayout.setSpacing(2)
        buttonBarLayout.setContentsMargins(5,0,5,0)

        # minArea contains sliders and buttons for each mineral that can be overlayed
        self.minArea = QWidget(controlArea)
        self.minAreaLayout = QVBoxLayout(self.minArea)
        self.minArea.setStyleSheet('background-color: rgb(40,44,52)')

        # adds buttonbar and minArea to controlArea
        controlAreaLayout.addWidget(buttonBar)
        controlAreaLayout.addWidget(self.minArea)

        # buttons and combobox used to select which corebox to display
        boxLabel = QLabel(buttonBar)
        boxLabel.setText('Core Box:')
        self.boxCB = QComboBox(buttonBar)
        self.boxCB.setFixedSize(75,30)
        self.boxCB.currentTextChanged.connect(lambda: self.changeCB())
        downBtn = QPushButton(buttonBar)
        downBtn.setText('˅')
        downBtn.setFixedWidth(20)
        downBtn.setStyleSheet('font: bold 6pt')
        downBtn.clicked.connect(lambda: self.downBox())
        upBtn = QPushButton(buttonBar)
        upBtn.setText('˄')
        upBtn.setFixedWidth(20)
        upBtn.setStyleSheet('font: bold 6pt')
        upBtn.clicked.connect(lambda: self.upBox())

        # add controls to buttonBarLayout
        buttonBarLayout.addWidget(boxLabel)
        buttonBarLayout.addWidget(self.boxCB)
        buttonBarLayout.addStretch()
        buttonBarLayout.addWidget(downBtn)
        buttonBarLayout.addWidget(upBtn)

        # container to hold core box images
        self.cbArea = QFrame(self)
        self.cbArea.setStyleSheet('background-color: rgb(0,0,0)')
        self.cbAreaLayout = QHBoxLayout(self.cbArea)

        # label that core box images and overlay can be painted onto
        self.coreBoxIm = QLabel(self.cbArea)
        self.cbAreaLayout.addStretch()
        self.cbAreaLayout.addWidget(self.coreBoxIm)
        self.cbAreaLayout.addStretch()

        # add container widgets to window layout
        layout.addWidget(self.cbArea)
        layout.addWidget(controlArea)

        # indicates the current core box in the display
        self.currentCb = []


    def setMinColors(self,inColors):
        """
         setMinColors takes inColors from the mainWindow class and converts them from
         hex to rgb values for the overlay.
         rgb values are stored in self.colors
        """
        for i in range(len(inColors)):
            hex = inColors[i][1:]                                        # remove '#' from hex value
            rgb = tuple(int(hex[j:j+2], 16) for j in (0, 2, 4))          # convert hex to rgb
            rgb = (np.asarray(rgb)*(255/np.max(rgb))).astype(np.uint8)   # convert tuple to numpy int array
            self.colors.append(rgb)                                      # add to colors list

    def downBox(self):
        """
         downBox reduces the value of boxCB, the combobox indicating the core box number, by 1
         called when downBtn is clicked
        """
        if self.boxCB.currentIndex() > 0:
            self.boxCB.setCurrentIndex(self.boxCB.currentIndex() - 1)

    def upBox(self):
        """
         upBox increases the value of boxCB, the combobox indicating the core box number, by 1
         called when upBtn is clicked
        """
        if self.boxCB.currentIndex() < self.boxCB.count() - 1:
            self.boxCB.setCurrentIndex(self.boxCB.currentIndex() + 1)

    def changeCB(self):
        """
         changeCB changes the corebox image displayed in the overlay window by geting the
         index of the new corebox and calling self.overlayIms()
         called when coreCB value is changed
        """

        self.currentCb = self.cbIms[self.boxCB.currentIndex()].toImage()
        self.overlayIms()

    def changeSlider(self,i):
        """
         changeSlider changes the opacity value displayed in mineral label i then redraws
         the overlay image with that opacity value by calling overlayIms()
         i is the index of the slider whose value changed
        """
        self.opSliderVals[i].setText(str(self.opSliders[i].value()) + '%')
        self.overlayIms()

    def addCoreIms(self, coreBoxIms, compMinList, compIms):
        """
         addCoreIms is called from the mainWindow class and used to pass corebox and core
         spectral images to the overlayView class
         inputs are the corebox and comp spectral images, list of mineral names, and the number
         of spectral images per corebox
        """

        self.cbIms = coreBoxIms                             # list of core box images
        self.compMinList = compMinList                      # list of comp spectral images
        self.compIms = compIms
        for i in range(len(coreBoxIms)):                    # adds list of indices for coreboxes to boxCB
            self.boxCB.addItem(str(i+1))

        # create lists of widgets for mineral overlay sliders, labels and buttons
        idx = []                                            # index of mineral
        opsWidgets = []                                     # list of container widets for overlay functions
        opsLayouts = []                                     # list of container widget layouts for overlay functions
        self.visButtons = []                                # list of mineral overlay visibility buttons
        self.opSliders = []                                 # list of mineral overlay oppacity sliders
        self.opSliderVals = []                              # lsit of mineral overlay oppacity sldier value labels

        for i in range(len(compMinList)):
            opsWidgets.append(QWidget(self.minArea))
            opsLayouts.append(QGridLayout(opsWidgets[i]))

            # pupulateMinWidget adds sldiers labesl and buttons to opsWidgets[i]
            self.pupulateMinWidget(opsWidgets[i], opsLayouts[i], i)

            self.minAreaLayout.addWidget(opsWidgets[i])

        self.minAreaLayout.addStretch()
        self.overlayIms()

    def pupulateMinWidget(self, parent, layout, idx):
        """
         pupulateMinWidget adds sldiers labesl and buttons to opsWidgets[i]
         need to do this in separate function so that the signals from buttons and opSliders
         remain separate
        """
        minLabel = QLabel(parent)
        minLabel.setText(self.compMinList[idx])

        # visibility button
        self.visButtons.append(QPushButton(parent))
        self.visButtons[idx].setText('Show')
        self.visButtons[idx].setCheckable(True)
        self.visButtons[idx].clicked.connect(lambda: self.overlayIms())

        # opacity slider
        self.opSliders.append(QSlider(Qt.Horizontal, parent))
        self.opSliders[idx].setMinimum(0)
        self.opSliders[idx].setMaximum(100)
        self.opSliders[idx].setValue(100)
        self.opSliders[idx].valueChanged.connect(lambda: self.changeSlider(idx))

        # oppacity sldier value labels
        self.opSliderVals.append(QLabel(parent))
        self.opSliderVals[idx].setText(str(100) + '%')

        # addwidget to opsWidgets layout
        layout.addWidget(minLabel,0,0)
        layout.addWidget(self.opSliderVals[idx],0,1)
        layout.addWidget(self.visButtons[idx],1,0)
        layout.addWidget(self.opSliders[idx],1,1)

    def overlayIms(self):
        """
         overlayIms draws the overlay pixmap on coreBoxIm using the corebox and mineral Images
        """

        # get index of  comp spectral images
        idx = self.boxCB.currentIndex()

        # get core box image
        cbIm = (self.cbIms[self.boxCB.currentIndex()].scaledToWidth(self.width()-350)).toImage()
        cbFormat = cbIm.format()

        # convert core box image to numpy array
        cbIm = qimage2ndarray.rgb_view(cbIm).copy()
        cbIm = cbIm.astype(np.float64)
        cbDim = cbIm.shape  # dimension of core box image array

        # create overlay mask
        overlay = cbIm * 0

        # max value of all mineral sliders
        maxSliderVal = 0

        for i in range(len(self.compMinList)):
            if self.visButtons[i].isChecked():
                startRow = 0        # starting row where to place comp spec image

                if self.opSliders[i].value() > maxSliderVal:    # change maxSliderVal if current slider larger
                    maxSliderVal = self.opSliders[i].value()

                minIm = self.compIms[self.compMinList[i]]['Images'][idx]   # get comp spec image
                minIm = minIm.scaledToWidth(cbDim[1]).toImage()        # scale to core box image width
                minIm = qimage2ndarray.rgb_view(minIm)                 # convert to ndarray
                minIm = minIm/np.amax(minIm)                           # normalize minIm dynamic range from 0-1
                minIm[minIm < 0.1] = 0                                 # remove overly dark pixels

                minDim = minIm.shape                                   # get dimension of comp spec image

                # multiply minIm by slider value % and the mineral's color rgb value
                minImOl = (self.opSliders[i].value()/100)*np.multiply(minIm,self.colors[i][:])

                # add minIm to the overlay
                overlay[startRow:startRow + minDim[0],:,:]  = overlay[startRow:startRow + minDim[0],:,:] + minImOl

                # get starting point for next comp spec image
                startRow = startRow + minDim[0] + 1

        # need to dim the pixels of core box images underneath the overlay
        flatIm = cbIm.min(axis=2)                                      # flatten the corebox image to get grayscale image
        nzIdx = np.nonzero(overlay)                                    # get index of nonzero pixels of overlay
        cbIm[nzIdx] = flatIm[nzIdx[0],nzIdx[1]]*((100-(maxSliderVal))/100) +  overlay[nzIdx] # replace pixels of corebox image underneath overlay with grayscale image and overlay

        # convert back to qimage
        outIm = qimage2ndarray.array2qimage(cbIm.astype(np.uint8))

        # set pixmap of coreBoxIm
        self.coreBoxIm.setPixmap(QPixmap(outIm))

    def resizeEvent(self,event):
        """
         resize overlay when window geometry changes
        """
        self.cbArea.setGeometry(self.cbArea.geometry())
