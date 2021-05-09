import os
import sys

import numpy as np
import qimage2ndarray
from natsort import natsorted, ns
from PIL import Image
from PySide2.QtCore import (QAbstractAnimation, QEvent, QMargins, QObject,
                            QPoint, QPropertyAnimation, QRect, QRectF, QSize,
                            Qt, Signal, Slot)
from PySide2.QtGui import (QBrush, QColor, QFont, QFontMetrics, QIcon, QImage,
                           QMouseEvent, QPainter, QPixmap, QTransform)
from PySide2.QtWidgets import (QAction, QApplication, QButtonGroup, QCheckBox,
                               QComboBox, QFileDialog, QFrame,
                               QGraphicsOpacityEffect, QGraphicsPixmapItem,
                               QGraphicsScene, QGraphicsView, QGridLayout,
                               QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                               QMainWindow, QMenu, QPushButton, QRadioButton,
                               QScrollArea, QSizePolicy, QSlider, QToolButton,
                               QVBoxLayout, QWidget)


def loadCsvData(mainDir, projName):
    """
    imports csv data and seperates into %, ppm, and geochemistry
    """

    # keep only the data and column names from the csv
    specData = np.genfromtxt(mainDir + '/' + projName + '_DATA.csv', delimiter=',', skip_header=4)
    dataNames = np.loadtxt(mainDir + '/' + projName + '_DATA.csv', delimiter=',', max_rows=1, dtype='str').tolist()
    units = np.genfromtxt(mainDir + '/' + projName + '_DATA.csv', delimiter=',', skip_header=1, max_rows=1, dtype='str')
    minVals = np.genfromtxt(mainDir + '/' + projName + '_DATA.csv', delimiter=',', skip_header=2, max_rows=1, dtype=np.uint16)
    maxVals = np.genfromtxt(mainDir + '/' + projName + '_DATA.csv', delimiter=',', skip_header=3, max_rows=1, dtype=np.uint16)

    # get mineral names data types
    minerals = []
    minDataTypes = []

    gcMinerals = []
    gcMinDataTypes = []

    for name in dataNames:
        if 'mineral_' in name:
            nameInfo = name.split('_')
            minerals.append(nameInfo[2])
            minDataTypes.append(nameInfo[1])
        elif 'Geochemistry_' in name:
            nameInfo = name.split('_')
            gcMinerals.append(nameInfo[2])
            gcMinDataTypes.append(nameInfo[1])

    minMeter = getMeter('Meter_mineral', specData, dataNames)
    gcMeter = getMeter('Meter_Geochemistry', specData, dataNames)

    minerals = natsorted(list(set(minerals)))
    minDataTypes = natsorted(list(set(minDataTypes)))

    gcMinerals = natsorted(list(set(gcMinerals)))
    gcMinDataTypes = natsorted(list(set(gcMinDataTypes)))

    minData = nestedDict(specData, dataNames, 'mineral_', minerals, minDataTypes, units, minVals, maxVals)
    gcMinData = nestedDict(specData, dataNames, 'Geochemistry_', gcMinerals, gcMinDataTypes, units, minVals, maxVals)

    return minData, gcMinData, minMeter, gcMeter

def nestedDict(data, dataList, dataType, minerals, minDataTypes, units, minVals, maxVals):
    """
    Creates a nested dictionary for mineral data that can be accessed using nestedDict['mineral name']['mineral data type'] 
    ex. mineral['Chlorite']['Wavelength']

    input:
    data - spectral data
    dataList - names of columns in spectral data set
    minerals - list of mineral names to be added to dict
    dataType - 'mineral_' or 'Geochemistry_' prefix in column name
    units - list of units for each data type
    minDataType - type of data to be added
    minVals - minimum data value for each data set (used to set axis limits in plots)
    maxVal -  maximum data value for each data set (used to set axis limits in plots)
    """

    nestDict = {}

    for i in range(len(minerals)):
        typeDict = {}
        for j in range(len(minDataTypes)):
            listItem = dataType + minDataTypes[j] + '_' + minerals[i]
            if listItem in dataList: 
                metaDict = {}
                specData = data[:,dataList.index(listItem)]

                metaDict['Data'] = specData 
                metaDict['Unit'] = units[dataList.index(listItem)]
                metaDict['Min'] = minVals[dataList.index(listItem)]
                metaDict['Max'] = maxVals[dataList.index(listItem)]

                typeDict[minDataTypes[j]] = metaDict

        nestDict[minerals[i]] = typeDict  

    return nestDict

def getMeter(meterName, data, dataList):
    """
    returns meter data from np array

    inputs"
    metername - indicates what meter to look for, should be 'Meter_mineral' or 'meter_Geochemistry'
    data - array of spectral data extracted from csv
    dataList - column names of spectral data 
    """
    meter = []

    if meterName in dataList:
        meter = data[:,dataList.index(meterName)]
        meter = np.round(meter, decimals = 1)   # round depts to 1 decimal place
        dim = data.shape
        meter = np.reshape(meter,(dim[0]))
        
    return meter

def getCoreImageNames(mainDir,rootDir,dirs):
    """
        returns the image names within directories dirs
    """

    imNameList = []
    numDirs = len(dirs)
    for i in range(numDirs):
        imDir = mainDir + '/' + dirs[i]
        os.chdir(imDir)
        imNameList.append(natsorted(os.listdir(imDir)))
        if i == 0:
            tempImList = natsorted(os.listdir(imDir))
            numIms = len(tempImList)
    os.chdir(rootDir)
    return imNameList, numIms

def getCoreImages(mainDir,numIms,dirs,dirDict,imNameList):
    """
        returns list of pixmap images from imNameList, found within directories dirs
    """

    imList = []
    numDirs = len(dirs)
    for i in range(numDirs):
        imDir = mainDir + '/' + dirs[i]
        tempImList = []
        for j in range(numIms):
            pixmap = QPixmap(imDir + '/' + imNameList[dirDict[dirs[i]]][j])
            tempImList.append(pixmap)
        imList.append(tempImList)
    return imList

def checkCoreDirs(numIms, intIms, compIms):
    """
        checks that there is the same number of core images in each Directory
    """

    checkPassed = True
    for i in range(len(intIms)):
        if len(intIms[i]) != numIms:
            checkPassed = False

    for i in range(len(compIms)):
        if len(compIms[i]) != numIms:
            checkPassed = False

    return checkPassed

def getCoreDims(imList, widgetHeight):
    """
        returns width of data widgets after scaling images
    """
    
    coreWidths = np.empty([len(imList[0]),len(imList)])
    coreHeights = np.empty([len(imList[0]),len(imList)])

    for j in range(len(imList)):
        for i in range(len(imList[j])):
            coreWidths[i,j] = imList[j][i].width()
            coreHeights[i,j] = imList[j][i].height()

    coreImWidth = np.max(coreWidths)
    coreImHeight = np.sum(coreHeights[:,0])

    coreImWidth = int(widgetHeight*coreImWidth/coreImHeight)

    return int(coreImWidth)

def getCoreBoxImageNames(mainDir, rootDir,dirs):
    """
        returns list of core box image names found in dirs
    """

    imDir = mainDir + '/' + dirs[0]
    os.chdir(imDir)
    imNameList = natsorted(os.listdir(imDir))
    os.chdir(rootDir)
    return imNameList

def getCoreBoxImages(mainDir, rootDir, dirs, imNameList):
    """
        returns core box images in dirs with names imNameList
    """

    imList = []
    imDir = mainDir + '/' + dirs[0]
    os.chdir(imDir)
    for j in range(len(imNameList)):
        pixmap = QPixmap(imNameList[j])
        # pixmapResized = pixmap.scaledToWidth(self.dataWidgetWidth)#, int(self.numCoresPerBox*self.coreHeight))
        imList.append(pixmap)
    os.chdir(rootDir)
    return imList
