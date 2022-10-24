from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QLabel,
    QComboBox,
    QPushButton,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
)
from PySide6.QtGui import (
    QPixmap,
    QColor,
    QBrush,
    QPixmap,
    QPainter,
    QColor,
    QFont,
    QTransform,
)
from PySide6.QtCore import (
    Qt,
    Signal,
    QPoint,
    QRect,
    QRectF,
    QMargins,
)
import numpy as np


class dhView(QWidget):
    """
    the dhView class is used to create the down-hole window which displays sections of drill
    core in zoomable (using mouse wheel) hoirzontal or vertical orientations
    uses zoomIm class to display images within the window
    """

    def __init__(self, parent):
        super(dhView, self).__init__(parent)
        """
         intializes widgets for down-hole view
        """

        # initialize image dimensions
        self.coreWidth = 0
        self.coreHeight = 0
        self.meterWidth = parent.meterWidth

        # set widget layout
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: rgb(0,0,0)")

        # content widget contains down-hole meter and images
        content = QWidget(self)
        self.contentLayout = QHBoxLayout(content)
        self.contentLayout.setSpacing(0)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        # button bar widget contains display options used to add imagery
        buttonBar = QFrame()
        buttonBar.setFixedHeight(30)
        buttonBar.setStyleSheet("background-color: rgb(40,44,52)")
        buttonBarLayout = QHBoxLayout(buttonBar)
        buttonBarLayout.setSpacing(2)
        buttonBarLayout.setContentsMargins(5, 0, 5, 0)

        # scroll are for the button bar, keeps buttons separated when app changes size
        buttonBarScroll = QScrollArea(self)
        buttonBarScroll.setFixedHeight(30)
        buttonBarScroll.setWidget(buttonBar)
        buttonBarScroll.setWidgetResizable(True)
        buttonBarScroll.verticalScrollBar().setEnabled(False)
        buttonBarScroll.horizontalScrollBar().setEnabled(True)
        buttonBarScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        buttonBarScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # scroll area for down-hole meter
        self.meterScroll = QScrollArea(content)
        self.meterScroll.setWidgetResizable(True)
        self.meterScroll.setFixedWidth(self.meterWidth)
        self.meterScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.meterScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # container for down-hole meter
        self.meterArea = QWidget()
        self.meterAreaLayout = QVBoxLayout(self.meterArea)
        self.meterAreaLayout.setSpacing(0)
        self.meterAreaLayout.setContentsMargins(0, 20, 0, 0)
        self.meterScroll.setWidget(self.meterArea)
        self.meterScroll.setAttribute(Qt.WA_TransparentForMouseEvents)

        # labels, comboboxes, and buttons for button bar
        startlabel = QLabel(buttonBar)
        startlabel.setText("Starting Depth:")
        self.startCB = QComboBox(buttonBar)  # combobox for depth start values
        self.startCB.setFixedSize(100, 30)
        self.startCB.currentIndexChanged.connect(lambda: self.startCBChanged())
        endLabel = QLabel(buttonBar)
        endLabel.setText("Ending Depth:")
        self.endCB = QComboBox(buttonBar)  # combobox for depth end values
        self.endCB.setFixedSize(100, 30)
        self.endCB.currentIndexChanged.connect(lambda: self.endCBChanged())
        self.typeCB = QComboBox(buttonBar)  # combobox for spectral image type
        self.typeCB.addItems(("Intensity", "Composition"))
        self.typeCB.setFixedSize(100, 30)
        self.typeCB.currentTextChanged.connect(lambda: self.changeCoreType())
        self.minCB = QComboBox(buttonBar)  # combobox for spectral image mineral
        self.minCB.setFixedSize(200, 30)
        rotButton = QPushButton(buttonBar)  # button used to rotate spectral images
        rotButton.setText("Rotate")
        rotButton.clicked.connect(lambda: self.rotateCores())
        addButton = QPushButton(
            buttonBar
        )  # adds images to zoomIm class in content widget
        addButton.setText("Add")
        addButton.clicked.connect(lambda: self.addCores())
        clearButton = QPushButton(
            buttonBar
        )  # removes images to zoomIm class in content widget
        clearButton.setText("Clear")
        clearButton.clicked.connect(lambda: self.clearWin())

        # add widgets to button bar
        buttonBarLayout.addWidget(startlabel)
        buttonBarLayout.addWidget(self.startCB)
        buttonBarLayout.addWidget(endLabel)
        buttonBarLayout.addWidget(self.endCB)
        buttonBarLayout.addStretch()
        buttonBarLayout.addWidget(self.typeCB)
        buttonBarLayout.addWidget(self.minCB)
        buttonBarLayout.addStretch()
        buttonBarLayout.addWidget(rotButton)
        buttonBarLayout.addStretch()
        buttonBarLayout.addWidget(addButton)
        buttonBarLayout.addWidget(clearButton)

        # custom class built to contain images
        self.zoomIm = zoomImage(content)

        # transparent widget positioned at top of down-hole window to contain headers
        self.headerArea = QWidget()
        self.headerArea.setStyleSheet("background-color: transparent")
        self.headerArea.setFixedHeight(20)
        self.headerAreaLayout = QHBoxLayout(self.headerArea)
        self.headerAreaLayout.setSpacing(1)
        self.headerAreaLayout.setContentsMargins(1, 0, 1, 0)
        self.headerAreaLayout.addStretch()
        self.headerAreaLayout.addStretch()

        # scroll area to contain headers
        self.headerAreaScroll = QScrollArea(content)
        self.headerAreaScroll.setWidget(self.headerArea)
        self.headerAreaScroll.setWidgetResizable(True)
        self.headerAreaScroll.move(self.meterWidth, 0)
        self.headerAreaScroll.setFixedHeight(20)
        self.headerAreaScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.headerAreaScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.headerAreaScroll.show()
        self.headerAreaScroll.raise_()
        self.headerAreaScroll.setStyleSheet(
            "Background-Color: transparent; border: 1px transparent"
        )
        self.headerAreaScroll.setAlignment(Qt.AlignCenter)

        # set the down-hole meter scrollbar max value to the zoomIm scrollbar max value, keeps images and meter aligned
        self.meterScroll.verticalScrollBar().setMaximum(
            self.zoomIm.verticalScrollBar().maximum()
        )

        # link the meter scrollbar with the zoomIm scrollbar
        self.zoomIm.verticalScrollBar().valueChanged.connect(
            self.meterScroll.verticalScrollBar().setValue
        )
        self.meterScroll.verticalScrollBar().valueChanged.connect(
            self.zoomIm.verticalScrollBar().setValue
        )

        # set the header scrollbar max value to the zoomIm scrollbar max value, keeps images and headers aligned
        self.zoomIm.horizontalScrollBar().setMaximum(10000)
        self.headerAreaScroll.horizontalScrollBar().setMaximum(10000)

        # link the header scrollbar with the zoomIm scrollbar
        self.zoomIm.horizontalScrollBar().valueChanged.connect(
            self.headerAreaScroll.horizontalScrollBar().setValue
        )

        # connect zoomed signal from zoomIm to function imageZoomed
        self.zoomIm.zoomed.connect(lambda: self.imageZoomed())

        # add meter and zoomIm to content widget
        self.contentLayout.addWidget(self.meterScroll)
        self.contentLayout.addWidget(self.zoomIm)

        # add content and buttonbar contatiners to down hole view window
        layout.addWidget(buttonBarScroll)
        layout.addWidget(content)

        # flags to track whether or not the window is empty and image orientation
        self.rotate = False

        # initialize lists of minerals and types displayed in zoomIm. These lists
        # are used to track what images need to be displayed in zoomIm whenever it
        # is zoomed or the cores or rotated
        self.typeList = []
        self.minList = []

    def changeCoreType(self):
        """
        function changes core drop down menu items (rgb<->mono) based on combobox state
        """
        self.minCB.clear()
        if self.typeCB.currentText() == "Intensity":
            self.minCB.addItems(self.intMinList)
        elif self.typeCB.currentText() == "Composition":
            self.minCB.addItems(self.compMinList)

    def setMeter(self, vals, numIms):
        """
        adds meter values to the start and end depth comboboxes
        """
        for i in range(0, len(vals), int(len(vals) / numIms)):
            cbVal = (
                "{:.1f}".format(vals[i]) + " m"
            )  # formats depth text to one decimal place and adds 'm'
            if i == 0:
                self.startCB.addItem(cbVal)
            else:
                self.startCB.addItem(cbVal)
                self.endCB.addItem(cbVal)
        self.endCB.addItem("{:.1f}".format(vals[-1]) + " m")
        self.endCB.setCurrentIndex(self.endCB.count() - 1)

    def addCoreIms(self, intMinList, intIms, compMinList, compIms):
        """
        adds spectral imagery to the down-hole view class
        """
        self.compMinList = compMinList  # list of composition image names
        self.compIms = compIms  # list of composition images
        self.intMinList = intMinList  # list of intentisty image names
        self.intIms = intIms  # list of composition images
        self.minCB.addItems(intMinList)  # adds intentisty images to mineral combobox

        # the rest of this function determines a common image size to display in zoomIm
        tempList = self.intIms + self.compIms

        for i in range(len(tempList)):
            for j in range(len(tempList[0])):
                if tempList[i][j].width() > self.coreWidth:
                    self.coreWidth = tempList[i][j].width()
                if tempList[i][j].height() > self.coreHeight:
                    self.coreHeight = tempList[i][j].height()

    def addCores(self):
        """
        adds the selected core images to the zoomIm
        """
        self.typeList.append(
            self.typeCB.currentText()
        )  # add the image's type to the typeList
        self.minList.append(self.minCB.currentText())  # add the mineral to the minList
        self.addImages()  # displays all images in typleList and minList on zoomIm
        # disable depth comboboxes until zoomIm is cleared
        self.startCB.setEnabled(False)
        self.endCB.setEnabled(False)

    def rotateCores(self):
        """
        rotates the cores within zoomIm by changing the rotate flag and redrawing the image
        """

        # change rotate flag
        if self.rotate == False:
            self.rotate = True
        elif self.rotate == True:
            self.rotate = False

        # add images to zoomIm if typeList contains data
        if self.typeList:
            self.addImages()

    def addImages(self):
        """
        adds images listed in typeList and minList to zoomIm. Called whenever add and rotate
        buttons are clicked or image is zoomed using the mousewheel
        """

        # clear the contents of zoomIm
        self.zoomIm.clear()

        # get index images using starting and ending coredepths
        startIdx = self.startCB.currentIndex()
        endIdx = self.endCB.currentIndex() + 1

        # initial image position within zoomIm
        xPos = 0
        yPos = 0

        # parse though minList and typeList to determine what images need to be added
        for j in range(len(self.typeList)):
            if self.typeList[j] == "Intensity":
                ims = self.intIms
                minIdx = self.intMinList.index(self.minList[j])
            elif self.typeList[j] == "Composition":
                ims = self.compIms
                minIdx = self.compMinList.index(self.minList[j])

            # starting y position of image
            yPos = 0

            for i in range(startIdx, endIdx):
                coreIm = QLabel()
                pixmap = ims[minIdx][i]
                tempXPos = 0
                # rotate images if rotate == true
                if self.rotate:
                    pixmapRotated = pixmap.transformed(QTransform().rotate(90))
                    pixmap = pixmapRotated.scaled(self.coreHeight, self.coreWidth)
                else:
                    pixmap = pixmap.scaled(self.coreWidth, self.coreHeight)

                # create a temporary pixmap item and add it to zoomIm
                temp = QGraphicsPixmapItem()
                temp.setPixmap(pixmap)
                self.zoomIm.scene.addItem(temp)
                temp.setY(yPos + 1)
                temp.setX(xPos + 1)

                # determine y position for next image
                yPos = yPos + pixmap.height()
                if tempXPos < pixmap.width():
                    tempXPos = pixmap.width()

            # determine x position for next set of images
            xPos = xPos + tempXPos

        # set viewport of zoomim to total image height and width
        self.zoomIm.imHeight = yPos
        self.zoomIm.imWidth = xPos
        self.zoomIm.setPhoto()

        # add down-hole meter and adjust scroll
        self.addZoomMeter()
        self.headerArea.setFixedWidth(
            self.zoomIm.mapFromScene(self.zoomIm.sceneRect()).boundingRect().width()
        )
        self.addHeader(
            int(
                self.zoomIm.mapFromScene(self.zoomIm.sceneRect()).boundingRect().width()
                / len(self.typeList)
            )
        )

    def drawMeter(self, width, height, fontSize):
        """
        draws pixmaps for down-hole meter. Maximum pixmap size is 32767 px so multiple pixmaps
        may be needed depending on core orientation, zoom level, and depth range
        """

        # determine number of pixmaps to produce
        numPixmaps = np.ceil(height / 32767).astype(int)

        # get values for meter from comboboxes
        startIdx = self.startCB.currentIndex()
        endIdx = self.endCB.currentIndex()
        numIms = abs(self.endCB.currentIndex() - self.startCB.currentIndex()) + 1
        meterVals = [self.startCB.itemText(i) for i in range(startIdx, endIdx + 1)]
        startVal = meterVals[0]
        startVal = float(startVal[:-1])
        endVal = meterVals[-1]
        endVal = float(endVal[:-1])

        # create and empty list for pixmaps
        pixmap = []

        # add pixmaps to list
        if numPixmaps == 1:
            pixmap.append(QPixmap(width, height))
        else:
            for i in range(numPixmaps):
                if i == (numPixmaps - 1):
                    pxHeight = height % (i * 32767)
                else:
                    pxHeight = 32767
                pixmap.append(QPixmap(width, pxHeight))

        # determine height of each meter tile
        ySpace = height / numIms
        newNumIms = numIms

        # optimize tile height
        while ySpace < 25 and newNumIms > 1:
            newNumIms = int(newNumIms / 2)
            ySpace = height / newNumIms

        # get list of strings for meter
        if newNumIms != numIms:
            numIms = newNumIms
            meterVals = []
            inc = (endVal - startVal) / (numIms - 1)
            for i in range(numIms):
                meterVals.append("{:.1f}".format(startVal + i * inc) + " m")

        # draw each meter tile
        imNum = 0
        for i in range(numPixmaps):
            qp = QPainter(pixmap[i])  # set painter on current pixmap
            qp.setBrush(QColor(0, 0, 0))
            qp.drawRect(0, 0, width, pixmap[i].height())  # draw black background
            qp.setBrush(QColor(222, 222, 222))
            qp.setPen(QColor(222, 222, 222))
            qp.setFont(QFont("Times", fontSize))

            # draw meter ticks and add text
            while imNum * ySpace < pixmap[i].height() + i * 32767 and imNum < numIms:
                qp.drawRect(20, imNum * ySpace - i * 32767, width - 20, 2)
                qp.drawText(
                    QPoint(0, imNum * ySpace - i * 32767 + int(1.5 * fontSize)),
                    meterVals[imNum],
                )
                imNum = imNum + 1

        return pixmap

    def addZoomMeter(self):
        """
        draws meter and adds to meterArea
        """
        # clear meter area
        for i in reversed(range(self.meterAreaLayout.count())):
            self.meterAreaLayout.itemAt(i).widget().deleteLater()

        # determine meter height and draw meter pixmaps
        meterHeight = (
            self.zoomIm.mapFromScene(self.zoomIm.sceneRect()).boundingRect().height()
        )
        meter = self.drawMeter(self.meterWidth, meterHeight, 10)

        # add meter pixmaps to meter area
        for i in range(len(meter)):
            tempLabel = QLabel(self.meterArea)
            tempLabel.setGeometry(meter[i].rect())
            tempLabel.setPixmap(meter[i])
            self.meterAreaLayout.addWidget(tempLabel)

        # set meter scrollbar value
        self.meterScroll.verticalScrollBar().setMaximum(
            self.zoomIm.verticalScrollBar().maximum()
        )

    def addHeader(self, width):
        """
        adds header and close button above each data widget
        """

        # remove headers
        if (
            self.headerAreaLayout.count() > 2
        ):  # > 2 because header area has two spacers at each end
            for i in reversed(range(1, self.headerAreaLayout.count() - 1)):
                self.headerAreaLayout.itemAt(i).widget().deleteLater()

        # make a header for each mineral in zoomIm
        for i in range(len(self.typeList)):
            self.makeHeader(width, self.minList[i], self.typeList[i], i)

        # set header scrollbar width
        self.headerAreaScroll.setFixedWidth(
            self.zoomIm.width() - self.zoomIm.verticalScrollBar().width()
        )

        # set maximum value of header and zoomIm scroll bars so that they scroll evenly together
        self.zoomIm.horizontalScrollBar().setMaximum(10000)
        self.headerAreaScroll.horizontalScrollBar().setMaximum(10000)

    def makeHeader(self, width, min, type, idx):
        """
        makes header widgets and places them above core images
        """

        # create container for header widgets
        windowHeader = QWidget()
        windowHeader.setFixedSize(width, 20)
        windowHeaderLayout = QHBoxLayout(windowHeader)
        windowHeaderLayout.setSpacing(0)
        windowHeaderLayout.setContentsMargins(0, 0, 0, 0)
        windowHeader.setStyleSheet("Background-Color: rgba(100,100,100,150)")

        # label for mineral name
        windowTitle = QLabel(windowHeader)
        windowTitle.setFixedHeight(20)
        windowTitle.setText(min + ", " + type)
        windowTitle.setStyleSheet(
            "background-color: transparent; font: bold 10pt; border: transparent"
        )

        # layout with stretch to centre titles
        windowHeaderLayout.addStretch()
        windowHeaderLayout.addWidget(windowTitle)
        windowHeaderLayout.addStretch()

        # add close button to header
        closeButton = QPushButton(windowHeader)
        closeButton.setText("X")
        closeButton.setFixedSize(20, 20)
        closeButton.setStyleSheet(
            "background-color: transparent; font: bold 10pt; border: transparent"
        )
        closeButton.clicked.connect(lambda: self.removeMin(idx))
        windowHeaderLayout.addWidget(
            closeButton
        )  # connect to closeButton which removes it from zoomIm

        # add header to headerArea
        self.headerAreaLayout.insertWidget(
            self.headerAreaLayout.count() - 1, windowHeader
        )

    def removeMin(self, idx):
        """
        Removes mineral images from zoomIm, typeList, and minList when close button clicked
        """

        # remove mineral and type from lists
        del self.typeList[idx]
        del self.minList[idx]

        # redraws zoomIm if there other images remain or clears zoomIm
        if len(self.minList) > 0:
            self.addImages()
        else:
            self.clearWin()

    def imageZoomed(self):
        """
        # reproducses meter and headers when zoomIm is zoomed using new image size
        """

        self.addZoomMeter()
        self.addHeader(
            int(
                self.zoomIm.mapFromScene(self.zoomIm.sceneRect()).boundingRect().width()
                / len(self.typeList)
            )
            - 2
        )
        self.headerArea.setFixedWidth(
            self.zoomIm.mapFromScene(self.zoomIm.sceneRect()).boundingRect().width()
        )
        self.zoomIm.horizontalScrollBar().setMaximum(
            10000
        )  # set maximum value of each scroll bar so that they scroll evenly together
        self.headerAreaScroll.horizontalScrollBar().setMaximum(10000)
        self.headerAreaScroll.horizontalScrollBar().setValue(
            self.zoomIm.horizontalScrollBar().value()
        )

    def clearWin(self):
        """
        completely clears contents of zoomIm, meterArea, and headerArea
        """
        for i in reversed(range(self.meterAreaLayout.count())):
            self.meterAreaLayout.itemAt(i).widget().deleteLater()
        if self.headerAreaLayout.count() > 2:
            for i in reversed(range(1, self.headerAreaLayout.count() - 1)):
                self.headerAreaLayout.itemAt(i).widget().deleteLater()
        self.startCB.setEnabled(True)
        self.endCB.setEnabled(True)
        self.zoomIm.clear()
        self.typeList = []
        self.minList = []
        self.zoomIm.zoom = 0

    def startCBChanged(self):
        """
        ensures that end depth value is higher than start depth when changed
        """
        if self.startCB.currentIndex() > self.endCB.currentIndex():
            self.endCB.setCurrentIndex(self.startCB.currentIndex())

    def endCBChanged(self):
        """
        ensures that start depth value is lower than end depth when changed
        """
        if self.endCB.currentIndex() < self.startCB.currentIndex():
            self.startCB.setCurrentIndex(self.endCB.currentIndex())

    def resizeEvent(self, event):
        """
        resizes the hearder area when the window size is changed
        """
        self.headerAreaScroll.setFixedWidth(
            self.zoomIm.width() - self.zoomIm.verticalScrollBar().width()
        )


class zoomImage(QGraphicsView):
    """
    The zoomImage class is used to display zoomable core images within the down-Hole
    view window.
    zoomImage has a zoom counter to keep track of zoom level
    """

    zoomed = Signal()  # signal used to let dhView know when image has been zoomed

    def __init__(self, parent):
        super(zoomImage, self).__init__(parent)
        """
         initialize the view's properties and scroll bars
        """
        self.setViewportMargins(QMargins(0, 20, 0, 0))
        self.zoom = 0  # initialize zoom level to 0
        self.empty = True  # tracks whether or not zoomimage contains an image
        self.scene = QGraphicsScene(self)  # initialize the QGraphicsScene
        self.photo = (
            QGraphicsPixmapItem()
        )  # initialize the QGraphicsPixmapItem, this will make up the image
        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setBackgroundBrush(QBrush(QColor(0, 0, 0)))  # color background black
        self.setFrameShape(QFrame.NoFrame)
        self.imHeight = 0  # initialize image height
        self.imWidth = 0  # initialize image width

    def clear(self):
        """
        removes any images from zoomImage and resets the scene, image height, and image width
        """
        if not self.empty:
            self.scene.clear()
            self.scene.clearFocus()
            self.empty = True
            self.imHeight = 0
            self.imWidth = 0
            self.setDragMode(QGraphicsView.NoDrag)
            self.resetTransform()

    def fitInView(self):
        """
        scales the image so that it fits entirely within the view and sets zoom to 0
        """

        # definte size of view
        rect = QRectF(QRect(0, 0, self.imWidth, self.imHeight))
        if not rect.isNull():
            self.setSceneRect(rect)
            if not self.empty:
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)

                if (
                    scenerect.height() < scenerect.width()
                    and scenerect.height() < 0.75 * viewrect.height()
                ):
                    factor = viewrect.width() / scenerect.width()
                    self.scale(factor, factor)
                else:
                    factor = viewrect.height() / scenerect.height()
                    self.scale(factor, factor)

                if self.mapFromScene(self.sceneRect()).boundingRect().height() < 25:
                    factor = (
                        25 / self.mapFromScene(self.sceneRect()).boundingRect().height()
                    )
                    self.scale(factor, factor)

                self.zoom = 0

    def setPhoto(self):
        """
        adds iamges to zoomImage
        """
        # set empty flag
        self.empty = False

        # sets image to be dragable with mouse
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        # sets the height of the scene
        self.setSceneRect(0, 0, self.imWidth, self.imHeight)

        # if zoom level was 0 scales image to fit in viewport, if not scales image to previous zoom level
        if self.zoom == 0:
            self.fitInView()
        else:
            tempZoom = self.zoom
            self.fitInView()
            factor = 1.25 ** (tempZoom)
            self.scale(factor, factor)
            self.zoom = tempZoom

        # ensures that images are at least 10 px wide
        while self.mapFromScene(self.sceneRect()).boundingRect().width() < 10:
            factor = 1.25
            self.scale(factor, factor)
            self.zoom += 1

        # sets the height of the scene and viewport
        self.setSceneRect(0, 0, self.imWidth, self.imHeight)
        self.viewport().setGeometry(0, 0, self.imWidth, self.imHeight)

    def wheelEvent(self, event):
        """
        enlarges or shrinks image when mousewheel signal is recieved
        if mousewheel delta >0 scale image 1.25x, zoom level +1
        if mousewheel delta <0 scale iamge 0.8x, zoom level -1
        """

        if not self.empty:
            if event.delta() > 0:
                height = self.mapFromScene(self.sceneRect()).boundingRect().height()
                if height < 1e6 and height < 10 * self.imHeight:
                    factor = 1.25
                    self.zoom += 1
                else:
                    factor = 1
            else:
                factor = 0.8
                self.zoom -= 1
            if self.zoom > 0:
                self.scale(factor, factor)
            elif self.zoom == 0:
                self.fitInView()
            else:
                self.zoom = 0

            # set viewport to new image size and emit zoomed signal
            self.viewport().setGeometry(
                0, 0, self.imWidth * factor, self.imHeight * factor
            )
            self.zoomed.emit()

    def resizeEvent(self, event):
        # resize zoomImage to image dimensiosn if window size changes
        self.setSceneRect(0, 0, self.imWidth, self.imHeight)
