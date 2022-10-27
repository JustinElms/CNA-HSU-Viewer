import os

import numpy as np
from natsort import natsorted
from PySide6.QtGui import QPixmap


def loadCsvData(mainDir, projName):
    """
    imports csv data and seperates into %, ppm, and geochemistry
    """

    # keep only the data and column names from the csv
    specData = np.genfromtxt(
        mainDir + "/" + projName + "_DATA.csv", delimiter=",", skip_header=4
    )
    dataNames = np.loadtxt(
        mainDir + "/" + projName + "_DATA.csv", delimiter=",", max_rows=1, dtype="str"
    ).tolist()
    units = np.genfromtxt(
        mainDir + "/" + projName + "_DATA.csv",
        delimiter=",",
        skip_header=1,
        max_rows=1,
        dtype="str",
    )
    minVals = np.genfromtxt(
        mainDir + "/" + projName + "_DATA.csv",
        delimiter=",",
        skip_header=2,
        max_rows=1,
        dtype=np.uint16,
    )
    maxVals = np.genfromtxt(
        mainDir + "/" + projName + "_DATA.csv",
        delimiter=",",
        skip_header=3,
        max_rows=1,
        dtype=np.uint16,
    )

    # get mineral names data types
    minerals = []
    minDataTypes = []

    gcMinerals = []
    gcMinDataTypes = []

    for name in dataNames:
        if "mineral_" in name:
            nameInfo = name.split("_")
            minerals.append(nameInfo[2])
            minDataTypes.append(nameInfo[1])
        elif "Geochemistry_" in name:
            nameInfo = name.split("_")
            gcMinerals.append(nameInfo[2])
            gcMinDataTypes.append(nameInfo[1])

    minMeter = getMeter("Meter_mineral", specData, dataNames)
    gcMeter = getMeter("Meter_Geochemistry", specData, dataNames)

    if len(minMeter) == 0:
        minMeter = getMeter("Info_Line_number", specData, dataNames)
        meterLoaded = False
    else:
        meterLoaded = True

    minerals = natsorted(list(set(minerals)))
    minDataTypes = natsorted(list(set(minDataTypes)))

    gcMinerals = natsorted(list(set(gcMinerals)))
    gcMinDataTypes = natsorted(list(set(gcMinDataTypes)))

    minData = nestedDict(
        specData, dataNames, "mineral_", minerals, minDataTypes, units, minVals, maxVals
    )
    gcMinData = nestedDict(
        specData,
        dataNames,
        "Geochemistry_",
        gcMinerals,
        gcMinDataTypes,
        units,
        minVals,
        maxVals,
    )

    return minData, gcMinData, minMeter, gcMeter, meterLoaded


def nestedDict(
    data, dataList, dataType, minerals, minDataTypes, units, minVals, maxVals
):
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
            listItem = dataType + minDataTypes[j] + "_" + minerals[i]
            if listItem in dataList:
                metaDict = {}
                specData = data[:, dataList.index(listItem)]

                metaDict["Data"] = specData
                metaDict["Unit"] = units[dataList.index(listItem)]
                metaDict["Min"] = minVals[dataList.index(listItem)]
                metaDict["Max"] = maxVals[dataList.index(listItem)]

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
        meter = data[:, dataList.index(meterName)]
        meter = np.round(meter, decimals=1)  # round depts to 1 decimal place
        dim = data.shape
        meter = np.reshape(meter, (dim[0]))

    return meter


def makeImDict(mainDir):

    subDirs = [f for f in os.scandir(mainDir) if f.is_dir()]

    imTypes = natsorted(list(set([f.name.split("_")[0] for f in subDirs])))

    imDict = {}
    for imType in imTypes:
        typeDict = {}
        for ims in subDirs:
            if imType in ims.name:
                minDict = {}
                minDict["Path"] = ims.path.replace("\\", "/")
                minDict["Images"] = []
                typeDict[ims.name.split("_")[1]] = minDict
        imDict[imType] = typeDict

    return imDict


def importMineralImages(imDict, imType, mineral):

    imDir = imDict[imType][mineral]["Path"]
    imNames = natsorted(os.listdir(imDir))

    imList = []
    for i in range(len(imNames)):
        pixmap = QPixmap(imDir + "/" + imNames[i])
        imList.append(pixmap)

    imDict[imType][mineral]["Images"] = imList

    return imDict


def checkNumIms(mainDir):
    subDirs = [f for f in os.scandir(mainDir) if f.is_dir()]

    checkPassed = True

    numIms = []
    for imDir in subDirs:
        imList = os.listdir(imDir.path)
        if not numIms:
            numIms = len(imList)
        elif len(imList) != numIms:
            checkPassed = 0
            numIms = 0
            return checkPassed, numIms

    return checkPassed, numIms


def getCoreDims(imList, widgetHeight):
    """
    returns width of data widgets after scaling images
    """

    coreWidths = np.empty(len(imList))
    coreHeights = np.empty(len(imList))

    for i in range(len(imList)):
        coreWidths[i] = imList[i].width()
        coreHeights[i] = imList[i].height()

    coreImWidth = np.max(coreWidths)
    coreImHeight = np.sum(coreHeights)

    coreImWidth = int(widgetHeight * coreImWidth / coreImHeight)

    return int(coreImWidth)
