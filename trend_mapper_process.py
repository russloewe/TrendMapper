# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TrendMapperDialog
                                 A QGIS plugin
 calculate trendlines along catagories
                             -------------------
        begin                : 2018-07-28
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Russell Loewe
        email                : russloewe@gmai.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.core import QgsMapLayerRegistry
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import QSqlDatabase
from PyQt4 import QtGui, uic, QtCore
from analysis import calculateLinearRegression #this needs to be param
from trend_mapper_tools import *

class TrendMapperProcess(QThread):
    def __init__(self, newLayer, stations, xField, yField, copyAttr):
        super(TrendMapperProcess, self).__init__()
        self.counter = 0
        self.totalCounter = len(stations)
        self.stations = stations
        self.copyAttr = copyAttr
        self.dataAttr = [xField, yField]
        self.xField = xField
        self.yField = yField
        self.newLayer = newLayer
        self.running = True
        self.stopSig = QtCore.SIGNAL("stopSignal")
        self.progSig = QtCore.SIGNAL("progress")
        self.msgSig = QtCore.SIGNAL ("msgSignal")
        self.abortSig = QtCore.SIGNAL('abortSignal')

            
    def abort(self):
        self.running = False
        self.emit(self.abortSig)
        self.emit(self.msgSig, 'Abort Called')
        
            
    def createConvFunction(self, formatDateCol, dateCol, dateForm):
        if formatDateCol:
            convFunction = convFunNum(self.dataAttr, dateColumn = dateCol,
                                            dateFormat = dateForm)
        else:
            convFunction = convFunNum(self.dataAttr)
        self.convFunction = convFunction
        
    def createDataFunction(self, layer, keyCol, statsCheck):
        def getdata(station):
            featureItr = featureGenerator(layer, station, keyCol)
            pointItr = datapointGenerator(featureItr, self.copyAttr + self.dataAttr)
            filterItr = filterDatapointGenerator(pointItr, filterFun)
            convItr = convertedDatapointGenerator(filterItr, 
                                       self.convFunction,
                                       skipOnErr = True)
            data = organizeData(convItr, self.dataAttr)
            for key in self.dataAttr:
                if (len(data[self.xField]) < 1) or (len(data[self.yField]) < 1):
                    return data, None
            result = calculateLinearRegression(data[self.xField], 
                                        data[self.yField],
                                    includeStats = statsCheck)
            return data, result
        self.getData = getdata
        
    def run(self):
        newFeatures = []
        self.firstRun = True
        for station in self.stations:
            if self.running == False:
                break
            else:
                self.process(station)
        self.emit(self.stopSig)
        
    def process(self, station):
        self.counter += 1
        self.updateProgress('Processing Datasets: ({})'.format(self.counter))
        #get result for one station
        data, result = self.getData(station)
        if result == None:
            return
        if self.firstRun:
            #add the add the result attributes as fields in new layer
            addResultFields(self.newLayer, result)
            firstRun = False
        mergeResult = mergeDicts(data, result, excluded = self.dataAttr)
        newFeature = makeFeature(self.newLayer, mergeResult)
        checkTrue(self.newLayer.startEditing())
        self.newLayer.addFeatures([newFeature], makeSelected = False)
        checkTrue(self.newLayer.commitChanges())

    def updateProgress(self, msg):
        progress = int(self.counter / float(self.totalCounter) * 100)
        self.emit(self.progSig, progress, msg)
    
