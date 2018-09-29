# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TrendMapperProcess
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
from trend_mapper_log import TrendMapperLogger
# Set the logger
log = TrendMapperLogger()

class TrendMapperProcess(QThread):
    '''A QT thread that does the main work for the plugin.
    
        **Signals**:
            - stopSig: Emit when the thread stops normally.
            - abortSig: Emit when the thread is told to stop early.
            - errSig: Emit when the thread stops from an error.
            - progSig: Emit when the thread updates the progress bar.
            - msgSig: Emit when the thread has a message for the message bar. 
            
        :param newLayer: The target layer for that the results of the 
            analysis.
        :type newLayer: QgsVectorLayer
        
        :param stations: The list of "stations" that we are analyzing
        :type stations: [str]
        
        :param xField: The name of the field for the independent variable 
            for the analysis.
        :type xField: str
        
        :param yField: The name of the field for the dependent variable 
            for analysis.
        :type yField: str
        
        :param copyAttr: A list of the other fields that are being copied to 
            the target layer.
        :type copyAttr: [str] 
        '''

    stopSig = QtCore.SIGNAL("stopSignal")
    progSig = QtCore.SIGNAL("progress")
    msgSig = QtCore.SIGNAL ("msgSignal")
    abortSig = QtCore.SIGNAL('abortSignal')
    errSig = QtCore.SIGNAL('errSignal')
    counter = 0
    running = True
    
    def __init__(self, newLayer, stations, xField, yField, copyAttr):

        super(TrendMapperProcess, self).__init__()
        self.totalCounter = len(stations)
        self.stations = stations
        self.copyAttr = copyAttr
        self.dataAttr = [xField, yField]
        self.xField = xField
        self.yField = yField
        self.newLayer = newLayer
        

            
    def abort(self):
        '''Tell the thread to stop running and send out an abort signal'''
        self.running = False
        self.emit(self.abortSig)
        self.emit(self.msgSig, 'Abort Called')
    
    def error(self, e):
        self.emit(self.abortSig)
        self.emit(self.errSig, str(e))
        return
            
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
        ''' Just call the woorkloop. Catch any error and emit an error signal.
        '''
        try:
            self.workloop()
        except Exception as e:
            self.error(e)
            
    def workloop(self):
        '''Iterate through the list of "stations", calling the process 
        function for each "stations".
        ''' 
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
    
