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


def loadCsvData(self):
    """
    imports csv data and seperates into %, ppm, and geochemistry
    """

    # keep only the data and column names from the csv
    specData = np.genfromtxt(self.mainDir + '/' + self.projName + '_DATA.csv', delimiter=',', skip_header=3)
    dataNames = np.loadtxt(self.mainDir + '/' + self.projName + '_DATA.csv', delimiter=',', max_rows=1, dtype='str').tolist()
    minVals = np.genfromtxt(self.mainDir + '/' + self.projName + '_DATA.csv', delimiter=',', skip_header=1, max_rows=1, dtype=np.uint16)
    maxVals = np.genfromtxt(self.mainDir + '/' + self.projName + '_DATA.csv', delimiter=',', skip_header=2, max_rows=1, dtype=np.uint16)

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

    minerals = natsorted(list(set(minerals)))
    minDataTypes = natsorted(list(set(minDataTypes)))

    gcMinerals = natsorted(list(set(gcMinerals)))
    gcMinDataTypes = natsorted(list(set(gcMinDataTypes)))


    # PUT THIS IN FN
    minData = {}

    for i in range(len(minerals)):
        tempDict = {}
        for j in range(len(minDataTypes)):
            listItem = 'mineral_' + minDataTypes[j] + '_' + minerals[i]
            if listItem in dataNames: 
                tempDict[minDataTypes[j]] = specData[:,dataNames.index(listItem)]
                tempDict[minDataTypes[j] +'_range'] = [minVals[dataNames.index(listItem)], maxVals[dataNames.index(listItem)]]
        minData[minerals[i]] = tempDict    

    gcMinData = {}

    for i in range(len(gcMinerals)):
        tempDict = {}
        for j in range(len(minDataTypes)):
            listItem = 'Geochemistry_' + minDataTypes[j] + '_' + minerals[i]
            if listItem in dataNames: 
                tempDict[minDataTypes[j]] = specData[:,dataNames.index(listItem)]
                tempDict[minDataTypes[j] +'_range'] = [minVals[dataNames.index(listItem)], maxVals[dataNames.index(listItem)]]
        gcMinData[minerals[i]] = tempDict   

    print('here')



    


def loadCsvDataOLD(self):
    """
        imports csv data and seperates into %, ppm, and geochemistry
    """

    # keep only the data and column names from the csv
    specData = np.genfromtxt(self.mainDir + '/' + self.projName + '_DATA.csv', delimiter=',', skip_header=1)
    dataNames = np.loadtxt(self.mainDir + '/' + self.projName + '_DATA.csv', delimiter=',', max_rows = 1, dtype='str')

    # get dimentions of data array
    dim = specData.shape

    # intialize data with zero np arrays
    self.perSpec = np.zeros([dim[0],1])                 # % spectral data
    self.ppmSpec = np.zeros([dim[0],1])                 # ppm spectral data
    self.waveSpec = np.zeros([dim[0],1])                # wavelength spectral data
    self.gcPerSpec = np.zeros([dim[0],1])               # geochemistry % data
    self.gcPpmSpec = np.zeros([dim[0],1])               # geochemistry ppm data
    self.gcWaveSpec = np.zeros([dim[0],1])              # geochemistry wavelength data

    # parse through the data and place it in the appropriate array
    for i  in range(len(dataNames)):
        if 'Meter_mineral' == dataNames[i]:
            self.minDepth = specData[:,[i]]
            self.minDepth = np.round(self.minDepth, decimals = 1)   # round depts to 1 decimal place
            self.minDepth = np.reshape(self.minDepth,(dim[0]))
        elif 'mineral_per_' in dataNames[i]:
            self.perSpecNames.append(dataNames[i].replace('mineral_per_',''))
            self.perSpec=np.append(self.perSpec,specData[:,[i]], axis=1)
        elif 'mineral_ppm_' in dataNames[i]:
            self.ppmSpecNames.append(dataNames[i].replace('mineral_ppm_',''))
            self.ppmSpec=np.append(self.ppmSpec,specData[:,[i]],axis=1)
        elif 'mineral_wavelength_' in dataNames[i]:
            self.waveSpecNames.append(dataNames[i].replace('mineral_wavelength_',''))
            self.waveSpec=np.append(self.waveSpec,specData[:,[i]],axis=1)
        elif 'Meter_Geochemistry' == dataNames[i]:
            self.gcDepth = specData[:,[i] ]
            self.gcDepth = np.round(self.gcDepth, decimals = 1)
            self.gcDepth = np.reshape(self.gcDepth,(dim[0]))
        elif 'Geochemistry_per_' in dataNames[i]:
            self.gcPerSpecNames.append(dataNames[i].replace('Geochemistry_per_',''))
            self.gcPerSpec=np.append(self.gcPerSpec,specData[:,[i]],axis=1)
        elif 'Geochemistry_ppm_' in dataNames[i]:
            self.gcPpmSpecNames.append(dataNames[i].replace('Geochemistry_ppm_',''))
            self.gcPpmSpec=np.append(self.gcPpmSpec,specData[:,[i]],axis=1)
        elif 'Geochemistry_wavelength_' in dataNames[i]:
            self.gcWaveSpecNames.append(dataNames[i].replace('Geochemistry_wavelength_',''))
            self.gcWaveSpec=np.append(self.gcWaveSpec,specData[:,[i]],axis=1)

    # remove NaNs in minDepth
    for i in range(len(self.minDepth)):
        if i > 0 and i < len(self.minDepth)-1 and  np.isnan(self.minDepth[i]) and ~np.isnan(self.minDepth[i+1]):
            self.minDepth[i] = np.mean([self.minDepth[i-1], self.minDepth[i+1]])
        elif i > 0 and  np.isnan(self.minDepth[i]):
            self.minDepth[i] = self.minDepth[i-1] + np.nanmean(np.diff(self.minDepth))

    # remove first value of arrays (garbage)
    self.perSpec = np.delete(self.perSpec,0,1)
    self.ppmSpec = np.delete(self.ppmSpec,0,1)
    self.waveSpec = np.delete(self.waveSpec,0,1)
    self.gcPerSpec = np.delete(self.gcPerSpec,0,1)
    self.gcPpmSpec = np.delete(self.gcPpmSpec,0,1)
    self.gcWaveSpec = np.delete(self.gcWaveSpec,0,1)

    # keep only real data in spectral data
    self.gcDepth = self.gcDepth[np.logical_not(np.isnan(self.gcDepth))]
    self.gcPerSpec = self.gcPerSpec[np.logical_not(np.isnan(self.gcPerSpec))]
    self.gcPpmSpec = self.gcPpmSpec[np.logical_not(np.isnan(self.gcPpmSpec))]
    self.gcWaveSpec = self.gcWaveSpec[np.logical_not(np.isnan(self.gcWaveSpec))]

    # remove NaNs from geochemistry meter
    if np.nanmax(self.gcDepth) < np.nanmax(self.minDepth):
        self.gcDepth = np.append(self.gcDepth, self.minDepth[-1])
        if self.gcPerSpec.size > 0:
            self.gcPerSpec = np.append(self.gcPerSpec, float("NAN"))
        if self.gcPpmSpec.size > 0:
            self.gcPpmSpec = np.append(self.gcPpmSpec, float("NAN"))
        if self.gcWaveSpec.size > 0:
            self.gcWaveSpec = np.append(self.gcWaveSpec, float("NAN"))

    # get a list of all minerals in _DATA.csv, sort and remove duplicates
    self.minList = natsorted(list(set(self.perSpecNames + self.ppmSpecNames + self.waveSpecNames + self.gcPerSpecNames + self.gcPpmSpecNames + self.gcWaveSpecNames)))

def getCoreImageNames(mainDir,rootDir,numIms,dirs):
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
    return imNameList

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
            pixmap = QPixmap(imdDir + '/' + imNameList[dirDict[dirs[i]]][j])
            tempImList.append(pixmap)
        imList.append(tempImList)
    return imList

def checkCoreDirs(self, intIms, compIms):
    """
        checks that there is the same number of core images in each Directory
    """

    checkPassed = True
    for i in range(len(intIms)):
        if len(intIms[i]) != self.numIms:
            checkPassed = False

    for i in range(len(compIms)):
        if len(compIms[i]) != self.numIms:
            checkPassed = False

    return checkPassed

def getCoreDims(self, imList):
    """
        returns total pixel height of all core images in imlist within a data widget after
        images have been scaled
    """

    coreWidths = np.empty([len(imList[0]),len(imList)])
    coreHeights = np.empty([len(imList[0]),len(imList)])
    for j in range(len(imList)):
        for i in range(len(imList[j])):
            coreWidths[i,j] = imList[j][i].width()
            coreHeights[i,j] = imList[j][i].height()

    self.coreImWidth = np.max(coreWidths)
    self.coreImHeight = np.sum(coreHeights[:,0])

    return int(self.coreImHeight*self.dataWidgetWidth/self.coreImWidth)

def getCoreBoxImageNames(self,dirs):
    """
        returns list of core box image names found in dirs
    """

    imDir = self.mainDir + '/' + dirs[0]
    os.chdir(imDir)
    imNameList = natsorted(os.listdir(imDir))
    os.chdir(self.rootDir)
    return imNameList

def getCoreBoxImages(self,dirs,imNameList):
    """
        returns core box images in dirs with names imNameList
    """

    imList = []
    imDir = self.mainDir + '/' + dirs[0]
    os.chdir(imDir)
    for j in range(len(imNameList)):
        pixmap = QPixmap(imNameList[j])
        # pixmapResized = pixmap.scaledToWidth(self.dataWidgetWidth)#, int(self.numCoresPerBox*self.coreHeight))
        imList.append(pixmap)
    os.chdir(self.rootDir)
    return imList
