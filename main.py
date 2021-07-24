import os
import sys

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from PySide2.QtCore import QPoint, Qt, Signal
from PySide2.QtGui import QIcon, QMouseEvent
from PySide2.QtWidgets import (QApplication, QButtonGroup, QCheckBox,
                               QComboBox, QFileDialog, QFrame, QGridLayout,
                               QGroupBox, QHBoxLayout, QLabel, QMainWindow,
                               QPushButton, QScrollArea, QSizePolicy, QSlider,
                               QVBoxLayout, QWidget)

try:
    # Include in try/except block if you're also targeting Mac/Linux
    from PySide2.QtWinExtras import QtWin
    myappid = 'CNA.HSUViewer.0.27'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

from drawing import *
from import_functions import *
from overlay_view import *


class mainWindow(QMainWindow):
    """
     mainWindow is the main class of the application.
     main window consists of an options drawer, down-hole meter, and data area (dashboard)
     two overlays are used to display data headers and a depth marker on top of the data
     area
    """

    drawerToggled = Signal()                                        # signal for when the drawer is opened or closed
    minColorChanged = Signal()                                      # signal for when a minerals color is changed
    zoomChanged = Signal()

    def __init__(self):
        super().__init__()
        """
         initializes widget sylesheets, image sizes, and lists of minerals and images.
         calls self.initUI() to create widgets
        """

        self.setStyleSheet("""
                    QWidget{
                        background-color: rgb(10,15,20);
                        color: rgb(222, 222, 222)
                    }
                    QWidget#drawer{
                       background-color: rgb(10,15,20);
                       border: 1px transparent;
                       color: rgb(222, 222, 222)
                    }
                    QToolTip{
                       background-color: rgb(10,15,20);
                       border: 1px solid rgb(222, 222, 222);
                       color: rgb(222, 222, 222)
                    }

                    QMainWindow{
                       background-color: rgb(10,15,20);
                       border: 1px transparent;
                       color: rgb(222, 222, 222)
                    }

                    QGroupBox#drawer{
                        background-color: rgb(10,15,20);
                        border: 1px solid rgb(222,222,222);
                        margin-top: 0.5em;
                    }
                    QGroupBox#drawer::title {
                        subcontrol-origin: margin;
                        left: 10px;
                        padding: 0 3px 0 3px;
                    }


                """)

        self.rootDir = os.getcwd()                                  # save the apps root directory for future reference
        screenGeometry = app.desktop().availableGeometry(self)      # gets screen resolution
        self.meterWidth = 60                                        # sets width of down hole meter to 3% of screen width
        self.startHeight = screenGeometry.height()-45 
        self.dataWidgetHeight = self.startHeight  
        self.startWidth = []      
        self.dataWidgetWidth = []                                   # initialize variable, gets corrected when data is loaded
        self.imDict = []

        # intialize lists for data, mineral names, and images
        self.intIms = []
        self.intMinList = []
        self.compIms = []
        self.compMinList = []
        self.minMeter = []
        
        # default colors for minerals in plots and overlay
        self.defaultColors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        self.plotColors = self.defaultColors.copy()
        self.setWindowIcon(QIcon('Icon.ico'))

        # set minimum size of app
        self.setMinimumSize(1000,750)

        # initialize app widgets
        self.initUI()

        # display app
        self.show()

    def initUI(self):
        """
         initUI creates the widgets for the application
        """

        os.chdir(self.rootDir)
        self.setWindowTitle("CNA Core Viewer v0.27")

        # create main widget and layout
        self.main = QWidget(self)
        self.setCentralWidget(self.main)
        mainLayout = QHBoxLayout(self.main)

        # widget for options drawer
        self.drawer = QWidget(self.main)
        self.drawerLayout = QHBoxLayout(self.drawer)
        self.drawerLayout.setSpacing(0)
        self.drawerLayout.setContentsMargins(0,0,0,0)

        # widget to contain drawer open/close button
        self.drawerButtonArea = QWidget(self.main)
        self.drawerButtonAreaLayout = QHBoxLayout(self.drawerButtonArea)
        self.drawerButtonArea.setStyleSheet('background-color: rgb(10,15,20)')
        self.drawerButtonArea.setFixedWidth(14)
        self.drawerButtonAreaLayout.setSpacing(0)
        self.drawerButtonAreaLayout.setContentsMargins(0,0,0,0)

        # create button to toggle drawer
        self.drawerButton = QPushButton(self.drawerButtonArea)
        self.drawerButton.setText('>')
        self.drawerButton.setFixedSize(10,500)
        self.drawerButton.clicked.connect(lambda: self.toggleDrawer())
        self.drawerButtonAreaLayout.addWidget(self.drawerButton)
        self.drawerButton.setStyleSheet('background-color: rgb(43,43,43); border: 1px solid rgb(222, 222, 222); border-radius : 5')

        # create area to display data
        self.contents = QWidget()
        contentsLayout = QHBoxLayout(self.contents)
        contentsLayout.setSpacing(0)
        contentsLayout.setContentsMargins(0,0,0,0)
        self.contents.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))

        # contentsScroll is used to keep widgets from getting compressed when app size changes, not scroll over contents.
        # mainScroll is used to scroll over widgets within contents
        self.contentsScroll = QScrollArea(self.main)
        self.contentsScroll.setWidget(self.contents)
        self.contentsScroll.setWidgetResizable(True)
        self.contentsScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.contentsScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # add widgets to main app
        mainLayout.addWidget(self.drawer)
        mainLayout.addWidget(self.drawerButtonArea)
        mainLayout.addWidget(self.contentsScroll)

        # headerArea is created to display data headers, sits on top over the contentsScroll
        self.headerArea = QWidget()
        self.headerArea.setFixedHeight(40)
        self.headerArea.setStyleSheet('background-color: transparent')
        self.headerArea.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))
        self.headerAreaLayout = QHBoxLayout(self.headerArea)
        self.headerAreaLayout.setSpacing(5)
        self.headerAreaLayout.setContentsMargins(0,0,0,0)
        self.headerAreaLayout.addStretch()

        # neter area will contain the down-hole meter
        self.meterArea= QWidget()
        self.meterAreaLayout = QVBoxLayout(self.meterArea)
        self.meterArea.setStyleSheet('Background-Color: rgb(0,0,0); border: transparent')

        # dataArea is nested inside contents, used to contain data widgets
        self.dataArea = QWidget()
        self.dataAreaLayout = QHBoxLayout(self.dataArea)
        self.dataAreaLayout.setSpacing(5)
        self.dataAreaLayout.setContentsMargins(0,0,0,0)
        self.dataAreaLayout.addStretch()
        self.dataArea.setStyleSheet('Background-Color: rgb(0,0,0)')

        # lineOverlay covers the entire contentsScroll area. used to display depth marker when meter is clicked
        self.lineOverlay = QWidget()
        self.lineOverlayLayout = QVBoxLayout(self.lineOverlay)
        self.lineOverlayLayout.setSpacing(0)
        self.lineOverlayLayout.setContentsMargins(0,0,0,0)
        self.lineOverlay.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.lineOverlay.setStyleSheet('Background-Color: transparent')

        # creates a label that the depth marker can be drawn onto
        self.lineLabel = QLabel(self.lineOverlay)
        self.lineLabel.setGeometry(0,0,self.lineOverlay.geometry().width(),3)
        self.lineLabel.setStyleSheet('Background-Color: rgba(255,0,0,100)')
        self.lineLabel.hide()

        # scroll area for the down-hole meter
        self.meterScroll = QScrollArea(self.contents)
        self.meterScroll.setWidget(self.meterArea)
        self.meterScroll.setWidgetResizable(True)
        self.meterScroll.setFixedWidth(self.meterWidth)
        self.meterScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.meterScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.meterScroll.setStyleSheet('border: 1px solid rgb(10, 10, 10)')
        contentsLayout.addWidget(self.meterScroll)

        # main scroll area for the data area
        self.mainScroll = QScrollArea(self.contents)
        self.mainScroll.setWidget(self.dataArea)
        self.mainScroll.setWidgetResizable(True)
        self.mainScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.mainScroll.setStyleSheet('Background-Color: black; border: 1px transparent')
        contentsLayout.addWidget(self.mainScroll)

        # scroll area for the data headers
        self.headerAreaScroll = QScrollArea(self.contents)
        self.headerAreaScroll.setWidget(self.headerArea)
        self.headerAreaScroll.setWidgetResizable(True)
        self.headerAreaScroll.move(self.meterWidth,0)
        self.headerAreaScroll.setFixedHeight(40)
        self.headerAreaScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.headerAreaScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.headerAreaScroll.show()
        self.headerAreaScroll.raise_()
        self.headerAreaScroll.setStyleSheet('Background-Color: transparent; border: 1px transparent')
        self.headerAreaScroll.setFixedWidth(self.mainScroll.width())

        # scroll area for the meter line overlay
        self.lineOverlayScroll = QScrollArea(self.contents)
        self.lineOverlayScroll.setWidget(self.lineOverlay)
        self.lineOverlayScroll.setGeometry(self.mainScroll.viewport().geometry())
        self.lineOverlayScroll.setWidgetResizable(True)
        self.lineOverlayScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.lineOverlayScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.lineOverlayScroll.show()
        self.lineOverlayScroll.raise_()
        self.lineOverlayScroll.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.lineOverlayScroll.setStyleSheet('Background-Color: transparent; border: 1px transparent')

        self.syncScrollBars()

        # set the maximum width of the drawer widget
        self.drawerWidth = 300
        self.drawer.setFixedWidth(self.drawerWidth)
        self.drawerButton.setText('<')

        # set flags to track when overlays and drawer are open
        self.drawerOpen = True
        self.zoomOpen = False
        self.dHViewOpen = False
        self.overlayWinOpen = False
        self.errorThrown = False
        self.colorMenuOpen = False

        # call initDrawerWidgets to initilize widgets inside of the drawer
        self.initDrawerWidgets()

        # maximized
        self.showMaximized()

    def initDrawerWidgets(self):
        """
         Adds widgets to sliding drawer. widgets are poupulated by 'newProject' function
        """

        # container for vertially stacked drawer widgets
        drawerVFrame = QFrame()
        drawerVFrame.setObjectName('drawer')
        drawerVLayout = QVBoxLayout(drawerVFrame)
        drawerVLayout.setSpacing(10)

        # scroll area to keep widgets from getting compressed when app changes size or if monitor is too small.
        # can be scrolled with mousewheel
        drawerScroll = QScrollArea(self.drawer)
        drawerScroll.setObjectName('drawer')
        drawerScroll.setWidget(drawerVFrame)
        drawerScroll.setWidgetResizable(True)
        drawerScroll.horizontalScrollBar().setEnabled(False)
        drawerScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        drawerScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.drawerLayout.addWidget(drawerScroll)

        # placeholder for drill hole identifier at top of drawer
        self.projBanner = QLabel(drawerVFrame, alignment=Qt.AlignCenter)
        self.projBanner.setFixedHeight(50)
        self.projBanner.setText(' ')

        # add 'open drill hole button'
        newProject = QPushButton(drawerVFrame)
        newProject.setText('Open Drill Hole')
        newProject.setStyleSheet("background-color: green; font: bold 12pt")
        newProject.clicked.connect(self.newProject)

        # add 'Down-Hole View' button
        # newDHViewButton = QPushButton(drawerVFrame)
        # newDHViewButton.setText('Down-Hole View')
        # newDHViewButton.setStyleSheet("background-color: grey; font: bold 12pt")
        # newDHViewButton.clicked.connect(lambda: self.openDHView())

        # add 'Open Core Overlay' button
        newOverlayButton = QPushButton(drawerVFrame)
        newOverlayButton.setText('Open Core Overlay')
        newOverlayButton.setStyleSheet("background-color: grey; font: bold 12pt")
        newOverlayButton.clicked.connect(lambda: self.openOverlayView())

        # group box for 'Add Spectral Images' functions
        newCoreGroupBox = QGroupBox("Add Spectral Images",drawerVFrame)
        newCoreGroupBoxLayout = QVBoxLayout(newCoreGroupBox)

        # comboboxes for the spectral image type options
        self.newCoreWindowCB = QComboBox(newCoreGroupBox)
        self.coreTypeCB = QComboBox(newCoreGroupBox)
        self.coreTypeCB.currentTextChanged.connect(lambda: self.changeCoreType())

        # button adds core images to contents widget
        addCoreButton = QPushButton("Add",drawerVFrame)
        addCoreButton.clicked.connect(lambda: self.initCoreWindow(self.coreTypeCB.currentText(), self.newCoreWindowCB.currentText()))
        addCoreButton.setStyleSheet('background-color: rgb(10,15,20); border: 1px solid rgb(222, 222, 222);')

        # add widgets to 'Add Spectral Images' group box
        newCoreGroupBoxLayout.addWidget(self.coreTypeCB)
        newCoreGroupBoxLayout.addWidget(self.newCoreWindowCB)
        newCoreGroupBoxLayout.addWidget(addCoreButton)

        # group box for 'Add Spectral Plot' options
        newSpecPlotGroupBox = QGroupBox("Add Spectral Plot",drawerVFrame)
        newSpecPlotGroupLayout = QVBoxLayout(newSpecPlotGroupBox)

        # combobox used to select plot type
        self.newSpecPlotWindowCB = QComboBox(newSpecPlotGroupBox)
        self.specPlotTypeCB = QComboBox(newSpecPlotGroupBox)
        self.newSpecPlotWindowCB.currentTextChanged.connect(lambda: self.changeSpecPlotMin(self.minData, self.newSpecPlotWindowCB.currentText(), self.specPlotTypeCB))
        
        # button adds plot widget to dashboard/main area
        addSpecPlotButton = QPushButton("Add",newSpecPlotGroupBox)
        addSpecPlotButton.clicked.connect(lambda: self.initSpectralPlotWindow(False))
        addSpecPlotButton.setStyleSheet('background-color: rgb(10,15,20); border: 1px solid rgb(222, 222, 222);')

        newSpecPlotGroupLayout.addWidget(self.newSpecPlotWindowCB)
        newSpecPlotGroupLayout.addWidget(self.specPlotTypeCB)
        newSpecPlotGroupLayout.addWidget(addSpecPlotButton)

        # group box for 'Add Geochemistry Plot' plot options
        newGcPlotGroupBox = QGroupBox("Add Geochemistry Plot",drawerVFrame)
        newGcPlotGroupLayout = QVBoxLayout(newGcPlotGroupBox)

        # comoboxes to select plot type
        self.newGcPlotWindowCB = QComboBox(newGcPlotGroupBox)
        self.gcPlotTypeCB = QComboBox(newGcPlotGroupBox)
        self.newGcPlotWindowCB.currentTextChanged.connect(lambda: self.changeSpecPlotMin(self.gcMinData, self.newGcPlotWindowCB.currentText(), self.gcPlotTypeCB))
        
        addGcPlotButton = QPushButton("Add",newGcPlotGroupBox)
        addGcPlotButton.clicked.connect(lambda: self.initSpectralPlotWindow(True))
        addGcPlotButton.setStyleSheet('background-color: rgb(10,15,20); border: 1px solid rgb(222, 222, 222);')

        newGcPlotGroupLayout.addWidget(self.newGcPlotWindowCB)
        newGcPlotGroupLayout.addWidget(self.gcPlotTypeCB)
        newGcPlotGroupLayout.addWidget(addGcPlotButton)

        # group box for 'Add Stacked Spectral Plot' options
        newStackPlotGroupBox = QGroupBox("Add Stacked Spectral Plot",drawerVFrame)
        self.newStackPlotGroupLayout = QVBoxLayout(newStackPlotGroupBox)

        # initialize mineral list for stack plots
        self.checkedList = []
        self.cBoxes = []

        # button adds plot widget to dashboard/main area
        addStackPlotButton = QPushButton("Add",newStackPlotGroupBox)
        addStackPlotButton.clicked.connect(lambda: self.initStackPlotWindow())
        addStackPlotButton.setStyleSheet('background-color: rgb(10,15,20); border: 1px solid rgb(222, 222, 222);')

        self.newStackPlotGroupLayout.addWidget(addStackPlotButton)

        zoomButtonFrame = QFrame()
        zoomButtonFramelayout = QHBoxLayout(zoomButtonFrame)

        zoomInButton = QPushButton('+')
        zoomInButton.clicked.connect(lambda: self.scaleDataWidgets(1))
        zoomInButton.setStyleSheet('background-color: rgb(10,15,20); border: 1px solid rgb(222, 222, 222);')
        zoomOutButton = QPushButton('-')
        zoomOutButton.clicked.connect(lambda: self.scaleDataWidgets(-1))
        zoomOutButton.setStyleSheet('background-color: rgb(10,15,20); border: 1px solid rgb(222, 222, 222);')
        
        zoomButtonFramelayout.addWidget(zoomOutButton)
        zoomButtonFramelayout.addWidget(zoomInButton)

        # add widgets to vertical layout
        drawerVLayout.addWidget(self.projBanner)
        drawerVLayout.addWidget(zoomButtonFrame)
        drawerVLayout.addWidget(newProject)
        drawerVLayout.addWidget(newCoreGroupBox)
        drawerVLayout.addWidget(newSpecPlotGroupBox)
        drawerVLayout.addWidget(newGcPlotGroupBox)
        drawerVLayout.addWidget(newStackPlotGroupBox)
        #drawerVLayout.addWidget(newDHViewButton)
        drawerVLayout.addWidget(newOverlayButton)
        
        # add mineral legend to bottom of drawer
        self.minColorButtonGroup = QButtonGroup()        # button group for mineral color swatches
        legendGroupBox = QGroupBox('Mineral Legend',drawerVFrame)
        legendGroupBoxlayout = QVBoxLayout(legendGroupBox)
        self.legendArea = QFrame(legendGroupBox)
        self.legendAreaLayout = QGridLayout(self.legendArea)
        legendGroupBoxlayout.addWidget(self.legendArea)
        drawerVLayout.addWidget(legendGroupBox)

        drawerVLayout.addStretch(1)

    def toggleDrawer(self):
        """
         when called toggleDrawer chanegs the size of the options drawer
        """
        if self.drawerOpen:
            self.drawer.setFixedWidth(0)
            self.drawerButton.setText('>')
            self.drawerOpen = False
        else:
            self.drawer.setFixedWidth(self.drawerWidth)
            self.drawerButton.setText('<')
            self.drawerOpen = True
        self.drawerToggled.emit()
        self.resizeOverlays()

    def resizeEvent(self,event):
        """
         function resizes overlay splash widgets and repositions their close buttons
        """

        self.resizeOverlays()
        self.syncScrollBars()

        if self.zoomOpen:
            self.overlayBG.setGeometry(0,0,self.width(),self.height())
            self.overlayCloseButton.move(self.width()-50,0)
            self.zoomWin.setGeometry(50,50,self.width()-100, self.height()-100)
        if self.overlayWinOpen:
            self.overlayBG.setGeometry(0,0,self.width(),self.height())
            self.overlayCloseButton.move(self.width()-50,0)
            self.overlayWin.setGeometry(50,50,self.width()-100, self.height()-100)
        if self.colorMenuOpen:
            self.minColorButtonGroup.button(idx).mapToGlobal(QPoint(10,10)) - self.main.mapToGlobal(QPoint(0,0))

    def syncScrollBars(self):   

        width = self.width()-self.mainScroll.verticalScrollBar().width()-self.drawer.width()-14
        self.headerAreaScroll.setFixedWidth(width-self.meterWidth)

        # set maximum value of each scroll bar so that they scroll evenly together
        self.mainScroll.horizontalScrollBar().setMaximum(1000)
        self.headerAreaScroll.horizontalScrollBar().setMaximum(1000)

        # sync main and meter scroll areas
        self.mainScroll.verticalScrollBar().valueChanged.connect(self.meterScroll.verticalScrollBar().setValue)
        self.meterScroll.verticalScrollBar().valueChanged.connect(self.mainScroll.verticalScrollBar().setValue)

        # sync main and lineoverlay scroll areas
        self.mainScroll.verticalScrollBar().valueChanged.connect(self.lineOverlayScroll.verticalScrollBar().setValue)
        self.lineOverlayScroll.verticalScrollBar().valueChanged.connect(self.mainScroll.verticalScrollBar().setValue)

        # sync main and header overlay scroll areas
        self.mainScroll.horizontalScrollBar().valueChanged.connect(self.headerAreaScroll.horizontalScrollBar().setValue)
        self.headerAreaScroll.horizontalScrollBar().valueChanged.connect(self.mainScroll.horizontalScrollBar().setValue)

    def resizeOverlays(self):
        """
         resizes the overlays themselves
         also called outside of resize event so keep as a seperate funciton
        """
        width = self.width()-self.mainScroll.verticalScrollBar().width()-self.drawer.width()-14
        self.headerAreaScroll.setFixedWidth(width-self.meterWidth)
        self.lineLabel.setFixedSize(width, 3)
        self.lineOverlay.setGeometry(0, 0, width, self.mainScroll.viewport().height())
        self.lineOverlayScroll.setGeometry(0, 0, width, self.mainScroll.viewport().height())

    def changeCoreType(self):
        """
         Changes the options in the 'Add Spectral Images' mineral combobox to match core type
        """
        if self.imDict.keys():
            self.newCoreWindowCB.clear()
            self.newCoreWindowCB.addItems(list(self.imDict[self.coreTypeCB.currentText()].keys()))

    def changeSpecPlotMin(self, minData, currentMin, typeCB):
        """
         function changes plot type combobox items based on mineral combobox state

         params:
         minData - dictionary of mineral data 
         currentMin - current value of mineral combobox
         typeCB - refernce to combobox containing data types 
        """

        typeCB.clear()
        cbVals = list(minData[currentMin].keys())
        for item in cbVals:
            if '_range' in item:
                cbVals.remove(item)

        typeCB.addItems(cbVals)

    def clearLayout(self,layout):
        """
         function clears widgets within a layout
        """

        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def throwError(self, message):
        """
         Displayes error message in a new overlay when called
         message is passed by trigger that calls this function
        """

        self.errorThrown = True
        self.overlayBG = QWidget(self)
        self.overlayBG.setGeometry(0,0,self.width(),self.height())
        self.overlayBG.setStyleSheet('Background-Color: rgba(0,0,0,200)')
        self.overlayBG.show()
        self.errorWin = QFrame(self.overlayBG)
        self.errorWin.setFixedSize(400,150)
        self.errorWin.setStyleSheet('Background-Color: rgb(10,15,20)')
        self.errorWinLayout = QVBoxLayout(self.errorWin)
        self.errorWinMessage = QLabel(self.errorWin)
        self.errorWinMessage.setText(message)
        self.errorWinMessage.setStyleSheet('Color: white; Background-Color: transparent; font: 16px')
        self.errorWinMessage.setAlignment(Qt.AlignCenter)
        self.errorWinLayout.addWidget(self.errorWinMessage)
        self.overlayCloseButton = QPushButton(self.overlayBG)
        self.overlayCloseButton.setText('x')
        self.overlayCloseButton.setStyleSheet('Background-Color: Transparent; font: 32pt')
        self.overlayCloseButton.setFixedSize(50,50)
        self.overlayCloseButton.move(self.width()-50,0)
        self.overlayCloseButton.show()
        self.overlayCloseButton.clicked.connect(lambda: self.closeOverlay(self.overlayBG, self.errorWin, self.overlayCloseButton))
        self.errorWin.move(int(self.width()/2-200),int(self.height()/2-75))
        self.errorWin.show()

    def newProject(self):
        """
         Loads images, data from csv, and creates widgets, scale, and drop down items
        """

        self.toggleDrawer()                                 # close options drawer
        self.selectMainDir()                                # prompt user to select core main directory

        if self.mainDir:
            #clear data from previous drill hole
            self.clearLayout(self.dataAreaLayout)
            self.clearLayout(self.headerAreaLayout)
            self.clearLayout(self.legendAreaLayout)

            # initilize lists for mineral images, mineral names, and spectral metrics
            self.intIms = []
            self.intMinList = []
            self.compIms = []
            self.compMinList = []

            # intialize lists for Stacked Spectral plot checkboxes
            self.checkedList = []
            self.cBoxes = []

            # clear data from comboboxes
            self.newCoreWindowCB.clear()
            self.newSpecPlotWindowCB.clear()
            self.newGcPlotWindowCB.clear()

            # clear previous stack plot checkboxes
            checkBoxes = self.newStackPlotGroupLayout.findChildren(QCheckBox)

            if checkBoxes:
                for i in range(len(checkBoxes)):
                    self.newStackPlotGroupLayout.removeWidget(checkBoxes[i])

            # change cursor to wait
            QApplication.setOverrideCursor(Qt.WaitCursor)

            # load spectral metric data from _DATA.csv
            self.minData, self.gcMinData, self.minMeter, self.gcMeter = loadCsvData(self.mainDir, self.projName)
            self.minList = list(self.minData.keys()) + list(self.gcMinData.keys())                                              # can this global var be removed? 

            self.imDict = makeImDict(self.mainDir)

            checkPassed, self.numIms = checkNumIms(self.mainDir)

            if checkPassed:
                # add drill hole name to top of options drawer
                self.projBanner.setText(" " + self.projName + " " )

                # adjust size of banner    FIND A BETTER WAY TO DO THIS
                if len(self.projName) <= 10:
                    self.projBanner.setStyleSheet("font: bold 22pt")
                elif len(self.projName) > 10 and len(self.projName) < 15:
                    self.projBanner.setStyleSheet("font: bold 16pt")
                elif len(self.projName) > 15 and len(self.projName) < 20:
                    self.projBanner.setStyleSheet("font: bold 12pt")

                # adjust height of data area
                self.dataArea.setFixedHeight(self.dataWidgetHeight)

                self.initMeter()
                #self.addCoreBoxes()

                # create a dictionary to map mineral to plot color
                self.plotColorDict = {self.minList[i]: self.plotColors[i] for i in range(len(self.minList))}

                # populate comoboxes
                self.coreTypeCB.addItems(list(self.imDict.keys()))
                self.newCoreWindowCB.addItems(list(self.imDict[self.coreTypeCB.currentText()].keys()))
                self.newCoreWindowCB.addItems(self.intMinList)
                self.newSpecPlotWindowCB.addItems(list(self.minData.keys()))
                self.newGcPlotWindowCB.addItems(list(self.gcMinData.keys()))

                # add checkboxes to Stacked Plot groupbox
                perSpecList = self.getPerSpecList()
                for i in range(len(perSpecList)):
                    specCBox = QCheckBox()
                    specCBox.setText(perSpecList[i])
                    specCBox.setChecked(True)
                    specCBox.min = perSpecList[i]
                    self.cBoxes.append(specCBox)
                    self.newStackPlotGroupLayout.insertWidget(self.newStackPlotGroupLayout.count()-1, specCBox)
                    self.checkedList.append(int(i))

                # add minerals to the mineral legend
                for i in range(len(list(self.minData.keys()))):
                    self.makeLegend(i)          # need to use function for each mineral to keep button signals seperate

                # restore the cursor and change directory back to root
                QApplication.restoreOverrideCursor()
                os.chdir(self.rootDir)

                try:
                    self.initCoreWindow('Photos','Medium-Resolution')
                except:
                    self.initCoreWindow(self.coreTypeCB.currentText(), self.newCoreWindowCB.currentText())
            else:
                # throw an error if missing images
                self.throwError('Missing core spectra images')

        self.toggleDrawer()

        self.resizeOverlays()

    def getPerSpecList(self):
        """
        returns list of minerals with percentage spectral metrics
        """
        perSpecList = []
        
        for mins in list(self.minData.keys()):
            if '%' in list(self.minData[mins].keys()):
                perSpecList.append(mins)

        return perSpecList 

    def getMineralDataTypes(self, minData):
        """
        returns datatypes of all minerals in a dictionary of mineral data
        
        params:
        minData - dictionary of mineral data structured as minData['mineral']['datatype']

        returns:
        typeList - lists of datatypes found in minData
        """
        typeList = []

        for min in list(minData.keys()):
            tempList = list(minData[min].keys())
            for item in tempList:
                if '_range' not in item:
                    typeList.append(item)

        typeList = natsorted(list(set(typeList)))     
        return typeList   

    def selectMainDir(self):
        """
         prompts user to slect the project directory and gets name of drill hole from directory
        """

        tempDir = str(QFileDialog.getExistingDirectory(self, "Select Main Directory"))
        if tempDir:     # check for valid directory
            tempName = tempDir.split("/")
            tempName = tempName[-1]
            dirContents = os.listdir(tempDir)

            # check to see that the main directory contaitns the data csv
            if tempName +'_DATA.csv' in dirContents:
                self.mainDir = tempDir
                self.projName = tempName
            else:
                self.mainDir = []
                self.throwError('Directory missing data file')
        else:
            self.mainDir = []

    def makeLegend(self, idx):
        """
         creates entries for the mineral legend in the options drawer including color swatch
         buttons.
         keep as seperate function so that signals remain unique
         idx is the index of the mineral in minList
        """
        colorButton = QPushButton()
        colorButton.setStyleSheet('background-color:' + self.plotColorDict[self.minList[idx]] + '; border: 1 px solid')
        colorButton.setFixedSize(10,10)
        colorButton.clicked.connect(lambda: self.changeMinColor(idx))
        legendLabel = QLabel(self.legendArea)
        legendLabel.setText(self.minList[idx])
        self.legendAreaLayout.addWidget(colorButton,idx,0)
        self.legendAreaLayout.addWidget(legendLabel,idx,1)
        self.minColorButtonGroup.addButton(colorButton)
        self.minColorButtonGroup.setId(colorButton,idx)

    def getMinDirs(self, dirType):
        """
         returns mineral directory names within mainDir
         dirType is prefix of directories, can be 'RGB_' or 'mineral_'
        """

        os.chdir(self.mainDir)
        subDirList = [dI for dI in os.listdir(self.mainDir) if os.path.isdir(os.path.join(self.mainDir,dI))]
        minDirs = natsorted([i for i in subDirList if dirType in i])
        os.chdir(self.rootDir)
        return minDirs

    def initMeter(self):
        """
        precursor to drawing the meter in meterArea. Needed so that the meter can be resized
        """
        self.addMeter()
        self.zoomChanged.connect(lambda: self.addMeter())

    def addMeter(self):
        """
         adds down-hole meter to meter area on main window
        """

        for i in reversed(range(self.meterAreaLayout.count())): 
            self.meterAreaLayout.itemAt(i).widget().deleteLater()

        # get numbers for meter ticks
        self.meterVals = self.getMeterDepths()
        self.meterLabel = QLabel(self.meterArea)
        #self.meterLabel.setFixedWidth(self.meterWidth)
        self.meterLabel.setFixedSize(self.meterWidth, self.dataWidgetHeight)
        self.meterLabel.setStyleSheet('Background-Color: rgb(0,0,0)')
        
        # produce pixmap of meter
        meter = drawMeter(self.meterVals, self.meterWidth, self.dataWidgetHeight)

        # set pixmap of meterLabel to meter pixmap
        self.meterLabel.setPixmap(meter[0])

        # set meterClicked flag false (i.e meter has not been clicked)
        self.meterClicked = False
        self.meterPos = 0                       # marker position for meter line
        self.lineOverlay.setFixedHeight(self.dataWidgetHeight)      # set height of meter line overlay

        # add label to meterArea and connect mouse click event
        self.meterAreaLayout.addWidget(self.meterLabel)
        self.meterAreaLayout.setContentsMargins(0,0,0,0)
        self.meterLabel.mouseReleaseEvent = lambda event: self.drawLine(event)

    def drawLine(self, event):
        """
         draws depth marker line across dataArea meter is clicked
        """

        if self.meterClicked == False:
            self.meterClicked = True
            self.meterPos = QMouseEvent.y(event)
            self.lineLabel.setGeometry(0,self.meterPos,self.lineOverlay.geometry().width(),3)
            self.lineLabel.show()
        else:
            self.meterClicked = False
            self.lineLabel.hide()

    def getMeterDepths(self):
        """
         returns values used for down-hole meter ticks
        """

        numPoints = self.numIms

        while numPoints * 20 > self.dataWidgetHeight:
            numPoints = numPoints / 2

        meterVals = np.arange(self.minMeter[0],self.minMeter[-1],(self.minMeter[-1]-self.minMeter[0])/(np.floor(numPoints)-1))
        meterVals = np.append(meterVals,self.minMeter[-1])

        return meterVals

    def addHeader(self, windowHeader, windowHeaderLayout, title, width, widget, axisStart, axisEnd):
        """
         adds header and close button above each data widget. title gives the text to
         display on the header, width is the width of the associated data widget,
         axis start and end are the minimum and maxiumim x axis values of plot widgets
        """

        # create container for widgets
        windowHeader.setFixedSize(width,40)             # 20 px for title and close button, 20 px for x axis limits
        windowHeader.setStyleSheet('background-color: transparent; border: transparent')

        # container for header title
        titleArea = QWidget(windowHeader)
        titleArea.setFixedHeight(20)
        titleArea.setStyleSheet('Background-Color: rgba(100,100,100,150)')
        titleAreaLayout = QHBoxLayout(titleArea)
        titleAreaLayout.setSpacing(0)
        titleAreaLayout.setContentsMargins(0,0,0,0)

        # label for header title
        windowTitle = QLabel(titleArea)
        windowTitle.setFixedHeight(20)
        windowTitle.setText(title)
        windowTitle.setStyleSheet('background-color: transparent; font: bold 10pt; border: transparent')

        titleAreaLayout.addWidget(windowTitle)

        # area for axis limits
        axisLabelArea = QWidget(self.headerArea)
        axisLabelArea.setFixedHeight(20)
        axisLabelAreaLayout = QHBoxLayout(axisLabelArea)
        axisLabelAreaLayout.setSpacing(0)
        axisLabelAreaLayout.setContentsMargins(0,0,0,0)

        # label for axis minimum
        axisStartLabel = QLabel(windowHeader)
        axisStartLabel.setFixedHeight(20)
        axisStartLabel.setStyleSheet('background-color: transparent; font: bold 10pt; border: transparent')
        axisStartLabel.setText(axisStart)

        # label for axis maximum
        axisEndLabel = QLabel(windowHeader)
        axisEndLabel.setFixedHeight(20)
        axisEndLabel.setStyleSheet('background-color: transparent; font: bold 10pt; border: transparent')
        axisEndLabel.setText(axisEnd)

        axisLabelAreaLayout.addWidget(axisStartLabel)
        axisLabelAreaLayout.addStretch()
        axisLabelAreaLayout.addWidget(axisEndLabel)

        windowHeaderLayout.addWidget(titleArea)
        windowHeaderLayout.addWidget(axisLabelArea)
        windowHeaderLayout.addStretch()

        titleAreaLayout.addStretch()
        titleAreaLayout.addWidget(windowTitle)
        titleAreaLayout.addStretch()

        # special header for core box images, does not include close button or axis limits
        if title != 'Core Box Images':
            closeButton = QPushButton(titleArea)
            closeButton.setText('X')
            closeButton.setFixedSize(20,20)
            closeButton.setStyleSheet('background-color: transparent; font: bold 10pt; border: transparent')
            closeButton.clicked.connect(lambda: self.closeWindow(widget, windowHeader, self.dataAreaLayout, self.headerAreaLayout))
            titleAreaLayout.addWidget(closeButton)

    def closeWindow(self,widget,header, widgetParentLayout, headerParentLayout):
        """
         function removes headers and widgets passed by arguments
        """

        widgetParentLayout.removeWidget(widget)
        headerParentLayout.removeWidget(header)
        widget.deleteLater()
        header.deleteLater()
        widget = None
        header = None

    def initCoreWindow(self, imType, mineral):
        """
            Creates container widgets for core images and associated header. Allows widgets to be resized with 
            zoomChanged method.

            params:
            imType - core image type as read from directory name
            mineral - mineral type as read from directory name

        """

        if imType and mineral:             # check to see that data has been loaded

            # create container widget for cores
            newDataWindow = QWidget(self.dataArea)
            newDataWindowLayout = QVBoxLayout(newDataWindow)
            newDataWindowLayout.setSpacing(0)
            newDataWindowLayout.setContentsMargins(0,20,0,0)

            # create container widget for header
            windowHeader = QWidget(self.headerArea)
            windowHeaderLayout = QVBoxLayout(windowHeader)
            windowHeaderLayout.setSpacing(0)
            windowHeaderLayout.setContentsMargins(0,0,0,0)
           
            # insert widget in dataArea
            if self.dataAreaLayout.count() == 0:
                self.dataAreaLayout.addWidget(newDataWindow)
                self.dataAreaLayout.addStretch()
            else:
                self.dataAreaLayout.insertWidget(self.dataAreaLayout.count()-1, newDataWindow)

            if self.headerAreaLayout.count() == 0:
                self.headerAreaLayout.addWidget(windowHeader)
                self.headerAreaLayout.addStretch()
            else:
                self.headerAreaLayout.insertWidget(self.headerAreaLayout.count()-1,windowHeader)

            self.addCoreWindow(newDataWindow, newDataWindowLayout, windowHeader, windowHeaderLayout, imType, mineral)
            self.zoomChanged.connect(lambda: self.resizeCoreWindow(newDataWindow, windowHeader))
        else:
            # throw area if data has not been loaded
            self.throwError('No Drill Hole Open')

    def resizeCoreWindow(self, dataWindow, header):
        dataWindow.setFixedSize(self.dataWidgetWidth, self.dataWidgetHeight)
        header.setFixedSize(self.dataWidgetWidth, 40)

    def addCoreWindow(self, newDataWindow, newDataWindowLayout, windowHeader, windowHeaderLayout, imType, mineral):
        """
         adds core spectral images to dataArea
        """

        self.clearLayout(newDataWindowLayout)
        self.clearLayout(windowHeaderLayout)

        if not self.imDict[imType][mineral]['Images']:
            self.imDict = importMineralImages(self.imDict, imType, mineral)
        ims = self.imDict[imType][mineral]['Images']

        if not self.dataWidgetWidth:
            self.startWidth = getCoreDims(self.imDict[imType][mineral]['Images'], self.dataWidgetHeight)
            self.dataWidgetWidth = self.startWidth

        newDataWindow.setFixedSize(self.dataWidgetWidth,self.dataWidgetHeight)

        # title for header
        title = mineral

        # creates header and places it in headerArea above data widget
        self.addHeader(windowHeader, windowHeaderLayout, title, self.dataWidgetWidth, newDataWindow, ' ', ' ')

        # displays zoom menu when right-clicking on data widget
        #newDataWindow.mouseReleaseEvent = lambda event: self.clickedCoreWidget(event,title,self.coreTypeCB.currentText())

        drawCoreImages(newDataWindow, newDataWindowLayout, title, ims)

    def closeOverlay(self, overlayBG, overlayMain, overlayCloseButton):
        """
         general close function used to close overlay specified by input arguements and
         set open flags to False
        """

        self.zoomOpen = False
        #self.dHViewOpen = False
        self.overlayWinOpen = False
        self.errorThrown = False
        overlayBG.deleteLater()
        overlayMain.deleteLater()
        overlayCloseButton.deleteLater()
        overlayBG = None
        overlayMain = None
        overlayCloseButton = None

    def initSpectralPlotWindow(self, gc):

        # check to see that data has been loaded from csv
        if self.minData or self.gcData:
            # create container widget for plot
            newDataWindow = QWidget(self.dataArea)
            newDataWindowLayout = QVBoxLayout(newDataWindow)
            newDataWindowLayout.setSpacing(0)
            newDataWindowLayout.setContentsMargins(0,20,0,0)

            newDataWindow.setVisible(False)
            self.dataAreaLayout.insertWidget(self.dataAreaLayout.count()-1, newDataWindow)
            newDataWindow.setVisible(True)

            # create container widget for header
            windowHeader = QWidget(self.headerArea)
            windowHeaderLayout = QVBoxLayout(windowHeader)
            windowHeaderLayout.setSpacing(0)
            windowHeaderLayout.setContentsMargins(0,0,0,0)

            if self.headerAreaLayout.count() == 0:
                self.headerAreaLayout.addWidget(windowHeader)
                self.headerAreaLayout.addStretch()
            else:
                self.headerAreaLayout.insertWidget(self.headerAreaLayout.count()-1,windowHeader)

            # check if metric belongs to geochemical data, get data, plot unit, and max X value
            if not gc:
                mineral = self.newSpecPlotWindowCB.currentText()
                dataType = self.specPlotTypeCB.currentText()
                plotSpec = self.minData[mineral][dataType]['Data']
                unit = self.minData[mineral][dataType]['Unit']
                xMin = self.minData[mineral][dataType]['Min']
                xMax = self.minData[mineral][dataType]['Max']
                plotDepth = self.minMeter

            # repeat same process for geochremistry sets
            elif gc:
                mineral = self.newGcPlotWindowCB.currentText()
                dataType = self.gcPlotTypeCB.currentText()
                plotSpec = self.gcMinData[mineral][dataType]['Data']
                unit = self.gcMinData[mineral][dataType]['Unit']
                xMin = self.gcMinData[mineral][dataType]['Min']
                xMax = self.gcMinData[mineral][dataType]['Max']
                plotDepth = self.gcMeter

            # cast 1d arrays to 2d arrays
            plotSpec = np.reshape(plotSpec,(np.amax(plotSpec.shape)))
            plotDepth = np.reshape(plotDepth,(np.amax(plotDepth.shape)))

            self.addSpectralPlotWindow(newDataWindow, newDataWindowLayout, windowHeader, windowHeaderLayout, mineral, plotSpec, plotDepth, xMin, xMax, unit)
            self.zoomChanged.connect(lambda: self.resizePlotWindow(newDataWindow, windowHeader))
        else:
            self.throwError('No Drill Hole Open')

    def resizePlotWindow(self, dataWindow, header):
        dataWindow.setFixedSize(self.dataWidgetWidth/2, self.dataWidgetHeight)
        header.setFixedSize(self.dataWidgetWidth/2, 40)

    def addSpectralPlotWindow(self, newDataWindow, newDataWindowLayout, windowHeader, windowHeaderLayout, mineral, plotSpec, plotDepth, xMin, xMax, unit):
        """
         adds spectral plot to dataArea
         
         Parms:
         gc - flag to indicate if data belongs to geochemistry set
        """

        self.clearLayout(newDataWindowLayout)
        self.clearLayout(windowHeaderLayout)

        newDataWindow.setFixedSize(self.dataWidgetWidth/2,self.dataWidgetHeight)

        # create plot figure and canvas
        plotFig = Figure(figsize=(self.dataWidgetWidth/100, (self.dataWidgetHeight-40)/100), dpi=100, facecolor = '#000000')
        plotCanvas = FigureCanvas(plotFig)
        plotCanvas.draw()
        plotCanvas.setMouseTracking(True)

        # make plot tooltip to display cursor coordinates and plot info
        plotCanvas.mouseMoveEvent = lambda event: self.makePlotToolTip(event, newDataWindow, 0, xMax, plotDepth[0], plotDepth[-1], unit, 'spec', ' ')

        # add widget to dataAera
        newDataWindowLayout.addWidget(plotCanvas)
        newDataWindowLayout.setSpacing(0)
        newDataWindowLayout.setContentsMargins(0,20,0,0)
        
        # draw plot and add slot which redraws if mineral color changes
        drawSpecPlot(plotFig, plotCanvas, plotSpec, xMin, xMax, plotDepth, self.plotColorDict[mineral], self.meterVals)
        self.minColorChanged.connect(lambda: drawSpecPlot(plotFig, plotCanvas, plotSpec, xMin, xMax, plotDepth, self.plotColorDict[mineral], self.meterVals))

        # add plot header to headerArea
        if unit == '%':
            xMax = xMax * 100

        self.addHeader(windowHeader, windowHeaderLayout, mineral, self.dataWidgetWidth/2, newDataWindow, "{:.1f}".format(xMin), "{:.1f}".format(xMax) +' ' + unit)

    def onClickedCBox(self):
        """
         keeps track of which check boxes are checked for drawing stacked plots
        """

        self.checkedList = []
        for i in range(len(self.cBoxes)):
            if self.cBoxes[i].isChecked():
                self.checkedList.append(self.cBoxes[i].text())
    
    def initStackPlotWindow(self):
        # check to see that data has been loaded from csv
        if self.minData:
            # create container widget for plot
            newDataWindow = QWidget(self.dataArea)
            newDataWindowLayout = QVBoxLayout(newDataWindow)
            newDataWindowLayout.setSpacing(0)
            newDataWindowLayout.setContentsMargins(0,20,0,0)

            newDataWindow.setVisible(False)
            self.dataAreaLayout.insertWidget(self.dataAreaLayout.count()-1, newDataWindow)
            newDataWindow.setVisible(True)

            # create container widget for header
            windowHeader = QWidget(self.headerArea)
            windowHeaderLayout = QVBoxLayout(windowHeader)
            windowHeaderLayout.setSpacing(0)
            windowHeaderLayout.setContentsMargins(0,0,0,0)

            if self.headerAreaLayout.count() == 0:
                self.headerAreaLayout.addWidget(windowHeader)
                self.headerAreaLayout.addStretch()
            else:
                self.headerAreaLayout.insertWidget(self.headerAreaLayout.count()-1,windowHeader)

            # create a temporary array to hold data from checked check boxes
            tempSpec = np.zeros([self.minMeter.shape[0],1])

            # add data to tempSpec
            for i in range(len(self.cBoxes)):
                if self.cBoxes[i].isChecked():
                    if np.sum(tempSpec) != 0:
                        tempSpec = np.c_[tempSpec, self.minData[self.cBoxes[i].text()]['%']['Data']]
                    else:
                        tempSpec[:,0] = self.minData[self.cBoxes[i].text()]['%']['Data']

            # replaces NaNs with 0s for stacked plot
            tempSpec = np.nan_to_num(tempSpec, copy=False, nan=0.0, posinf=None, neginf=None)
            specDim = tempSpec.shape

            #  create plotSpec for stacked data
            plotSpec = np.zeros([specDim[0], specDim[1]+1])
            plotSpec[:,0] = tempSpec[:,0]

            # stack data by adding each column to the one before it, except last column
            for i in range(1,specDim[1]+1):
                if i < specDim[1]:
                    plotSpec[:,i] = tempSpec[:,i] + plotSpec[:,i-1]
                else:
                    plotSpec[:,i] = np.ones([specDim[0]])

            plotColor = []
            plotMinNames = []

            # get list of colors for plots
            for i in range(len(self.cBoxes)):
                if self.cBoxes[i].isChecked():
                    plotColor.append(self.plotColors[self.minList.index(self.cBoxes[i].text())])
                    plotMinNames.append(self.cBoxes[i].text())

            self.addStackPlotWindow(newDataWindow, newDataWindowLayout, windowHeader, windowHeaderLayout, plotSpec, specDim, plotColor, plotMinNames)
            self.zoomChanged.connect(lambda: self.resizePlotWindow(newDataWindow, windowHeader))

        else:
            self.throwError('No Drill Hole Open')

    def addStackPlotWindow(self, newDataWindow, newDataWindowLayout, windowHeader, windowHeaderLayout, plotSpec, specDim, plotColor, plotMinNames):
        """
         adds stacked plot to dataArea, only uses data from percentage metrics
        """

        self.clearLayout(newDataWindowLayout)
        self.clearLayout(windowHeaderLayout)

        # create a legend for the toolTip
        tag = ' '
        for i in range(len(plotMinNames)):
            tag = tag  + '<font color="' + plotColor[i] + '">■</font> ' + plotMinNames[i]
            if i != len(plotMinNames)-1:
                tag = tag + '<br>'

        # check to see that data has been loaded from csv
        newDataWindow.setFixedSize(self.dataWidgetWidth/2,self.dataWidgetHeight)

        # create plot figure and canvas
        plotFig = Figure(figsize=(self.dataWidgetWidth/100, (self.dataWidgetHeight-40)/100),dpi=100,facecolor ='#000000')
        plotCanvas = FigureCanvas(plotFig)
        plotCanvas.draw()

        plotCanvas.setMouseTracking(True)
        plotCanvas.mouseMoveEvent = lambda event: self.makePlotToolTip(event, plotCanvas, 0, 100, self.minMeter[0], self.minMeter[-1], '%', 'stack', tag)

        # add widget to dataArea
        newDataWindowLayout.addWidget(plotCanvas)

        # add plot header to headerArea
        self.addHeader(windowHeader, windowHeaderLayout, ' ', self.dataWidgetWidth/2, newDataWindow, '0', '100 %')

        # draw plot and add slot which redraws if mineral color changes
        drawStackPlot(plotFig, plotCanvas, plotSpec, specDim, plotColor, plotMinNames, self.minMeter, self.meterVals)
        self.minColorChanged.connect(lambda: drawStackPlot(plotFig, plotCanvas, plotSpec, specDim, plotColor, plotMinNames, self.minMeter, self.meterVals))

    def makePlotToolTip(self, event, parent, minX, maxX, minY, maxY, unit, plotType, legend):
        """
         displays depth and plot values in tooltip, takes axis ranges, plot units, type,
          and the legend to display
        """

        # checks to see that mouse is over plot and adds data to tooltip
        if event.y() > 20 and event.y()<self.dataWidgetHeight-20: 
            yPos = minY + (event.y()-20)*(maxY-minY)/(self.dataWidgetHeight-40)
            xPos = minX + (event.x())*maxX/(self.dataWidgetWidth/2)

            if plotType == 'spec':
                parent.setToolTip("{:.1f}".format(yPos) + ' m, ' + "{:.1f}".format(xPos) + ' ' + unit )
            elif plotType == 'stack':
                parent.setToolTip("{:.1f}".format(yPos) + ' m, ' + "{:.1f}".format(xPos) + ' ' + unit + '<br>' + legend)

    def openOverlayView(self):
        """
         Opens a mineral overaly view window when the 'Overlay View' button is clicked
        """

        # check to see that data has been loaded
        if self.intMinList or self.compMinList:

            # draw semi transparent background for splash window
            self.overlayBG = QWidget(self)
            self.overlayBG.setGeometry(0,0,self.width(),self.height())
            self.overlayBG.setStyleSheet('Background-Color: rgba(0,0,0,200)')
            self.overlayBG.show()

            # add close button to top right of app, just outside down-hole view window
            self.overlayCloseButton = QPushButton(self.overlayBG)
            self.overlayCloseButton.setText('x')
            self.overlayCloseButton.setStyleSheet('Background-Color: Transparent; font: 32pt')
            self.overlayCloseButton.setFixedSize(50,50)
            self.overlayCloseButton.move(self.width()-50,0)
            self.overlayCloseButton.show()

            # add overlay view window over applicaiton
            self.overlayWin = overlayView(self)
            # get colors of overlay minerals
            overlayColors = []
            for i in range(len(self.compMinList)):
                overlayColors.append(self.plotColors[self.minList.index(self.compMinList[i])])
            self.overlayWin.setMinColors(overlayColors)         # pass colors to overlayView class
            self.overlayWin.setGeometry(50,50,self.width()-100, self.height()-100)
            self.overlayWinOpen = True
            self.overlayWin.addCoreIms(self.medResIms, self.compMinList, self.compIms, self.numCoresPerBox)  # pass images and names to overlayView class
            self.overlayWin.show()

            # connect the close button
            self.overlayCloseButton.clicked.connect(lambda: self.closeOverlay(self.overlayBG, self.overlayWin, self.overlayCloseButton))
        else:
            self.throwError('No Drill Hole Open')

    def changeMinColor(self, idx):
        """
         creates a widget with rgb sliders so the user can adjsut the minerals plot colors
         called when user clickes on a color swatch in the mineral legend
         idx refers to the affected mineral
        """

        if not self.colorMenuOpen:                      # check if a color menu is already open
            hex = self.plotColors[idx][1:]              # get current mineral color
            rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))             # convert hex to rgb

            # create color options widget
            colorMenu = QWidget(self)
            colorMenu.setFixedSize(self.dataWidgetWidth, int(self.dataWidgetWidth/3))
            colorMenuLayout = QVBoxLayout(colorMenu)
            colorMenuLayout.setSpacing(0)
            colorMenuLayout.setContentsMargins(0,0,0,0)

            # area for rgb sliders
            sliderArea = QWidget(colorMenu)
            sliderAreaLayout = QGridLayout(sliderArea)

            # area for two buttons
            buttonArea = QWidget(colorMenu)
            buttonAreaLayout = QHBoxLayout(buttonArea)

            # labels for sldiers
            rLabel = QLabel(sliderArea)
            rLabel.setText('R')
            gLabel = QLabel(sliderArea)
            gLabel.setText('G')
            bLabel = QLabel(sliderArea)
            bLabel.setText('B')

            # create rgb sliders
            rSlider = QSlider(Qt.Horizontal,sliderArea)
            rSlider.setMinimum(0)
            rSlider.setMaximum(255)
            rSlider.setValue(rgb[0])

            gSlider = QSlider(Qt.Horizontal,sliderArea)
            gSlider.setMinimum(0)
            gSlider.setMaximum(255)
            gSlider.setValue(rgb[1])

            bSlider = QSlider(Qt.Horizontal,sliderArea)
            bSlider.setMinimum(0)
            bSlider.setMaximum(255)
            bSlider.setValue(rgb[2])

            # create labels to indicate current sldier value
            rValueLabel = QLabel(sliderArea)
            rValueLabel.setText(str(rSlider.value()))
            gValueLabel = QLabel(sliderArea)
            gValueLabel.setText(str(gSlider.value()))
            bValueLabel = QLabel(sliderArea)
            bValueLabel.setText(str(bSlider.value()))

            # connect sldiers to sliderColorChanged function
            rSlider.valueChanged.connect(lambda: self.sliderColorChanged(rSlider.value(),gSlider.value(),bSlider.value(),rValueLabel,rSlider.value(),idx))
            gSlider.valueChanged.connect(lambda: self.sliderColorChanged(rSlider.value(),gSlider.value(),bSlider.value(),gValueLabel,gSlider.value(),idx))
            bSlider.valueChanged.connect(lambda: self.sliderColorChanged(rSlider.value(),gSlider.value(),bSlider.value(),bValueLabel,bSlider.value(),idx))

            # add widgets to sldierArea
            sliderAreaLayout.addWidget(rLabel,0,0)
            sliderAreaLayout.addWidget(rSlider,0,1)
            sliderAreaLayout.addWidget(rValueLabel,0,2)
            sliderAreaLayout.addWidget(gLabel,1,0)
            sliderAreaLayout.addWidget(gSlider,1,1)
            sliderAreaLayout.addWidget(gValueLabel,1,2)
            sliderAreaLayout.addWidget(bLabel,2,0)
            sliderAreaLayout.addWidget(bSlider,2,1)
            sliderAreaLayout.addWidget(bValueLabel,2,2)

            # add sldier and button layouts to color menu
            colorMenuLayout.addWidget(sliderArea)
            colorMenuLayout.addWidget(buttonArea)

            # get current location of bottom right of color swatch
            pos = self.minColorButtonGroup.button(idx).mapToGlobal(QPoint(10,10)) - self.main.mapToGlobal(QPoint(0,0))

            # add buton to restore default mineral color
            defaultButton = QPushButton(buttonArea)
            defaultButton.setText('Restore Default')
            defaultButton.clicked.connect(lambda: self.restoreDefaultColor(rSlider,gSlider,bSlider,idx))

            # add button to apply chagnes to all widgets
            applyButton = QPushButton(buttonArea)
            applyButton.setText('Apply')
            applyButton.clicked.connect(lambda: self.applyColorChange(rSlider.value(),gSlider.value(),bSlider.value(),idx,colorMenu))

            # add buttons to button area
            buttonAreaLayout.addWidget(defaultButton)
            buttonAreaLayout.addWidget(applyButton)

            # dsiplay color menu and move to bottom right coener of color swatch
            colorMenu.show()
            colorMenu.move(pos.x(), pos.y())

            # set flag to show the menu is open
            self.colorMenuOpen = True

    def sliderColorChanged(self,r,g,b,label,val,idx):
        """
         function changes the values displayed in the color slider labels and changes the
         color currently displayed in teh swatch only
         called when sliders change value
         takes current values of rgb sliders, reference to the value label, value of slider
         that changed, and index of the mineral and button
        """
        self.minColorButtonGroup.button(idx).setStyleSheet('background-color: rgb(' + str(r) + ',' + str(g) + ',' + str(b) + '); border: 1 px solid')
        label.setText(str(val))

    def restoreDefaultColor(self,rSlider,gSlider,bSlider,idx):
        """
         function restores the default collor of the selected mineral
         arguements are references to the three color sliders and idx of the affected mineral
        """

        hex = self.defaultColors[idx][1:]
        self.plotColors[idx] = hex
        self.plotColorDict = {self.minList[i]: self.plotColors[i] for i in range(len(self.minList))}
        rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
        rSlider.setValue(rgb[0])
        gSlider.setValue(rgb[1])
        bSlider.setValue(rgb[2])
        self.minColorButtonGroup.button(idx).setStyleSheet('background-color: rgb(' + str(rgb[0]) + ',' + str(rgb[1]) + ',' + str(rgb[2]) + '); border: 1 px solid')

    def applyColorChange(self,r,g,b,idx,colorMenu):
        """
         function sends signal to data widgets when a mineral's plot color is changeSlider
         inputs are rgb values of new color, index of the affected mineral, and references
         the the color menu
        """
        # convert rgb values to hex and add to color list and dictionary
        hex = '#%02x%02x%02x' % (r,g,b)
        self.plotColors[idx] = hex
        self.plotColorDict = {self.minList[i]: self.plotColors[i] for i in range(len(self.minList))}

        # delete the color menu, change the colorMenuOpen flag, and emit the color changed signal
        colorMenu.deleteLater()
        self.colorMenuOpen = False
        self.minColorChanged.emit()

    def scaleDataWidgets(self, factor):
        """
        Function changes the size of widgets in the dashboard
        """

        if self.imDict:
            newHeight = self.dataWidgetHeight * (1.25 ** factor)
            newWidth = self.dataWidgetWidth * (1.25 ** factor)

            if newHeight < 32767 and newHeight < 10 * self.startHeight:
                if newHeight < self.startHeight:
                    newHeight = self.startHeight
                    newWidth = self.startWidth

                self.dataWidgetHeight = newHeight
                self.dataWidgetWidth = newWidth
                self.dataArea.setFixedHeight(self.dataWidgetHeight)
                self.syncScrollBars()

                self.zoomChanged.emit()

                self.update()

if __name__ == '__main__':
    # Handle high resolution displays:
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    ex = mainWindow()
    app.exec_()
