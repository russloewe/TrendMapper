# -*- coding: utf-8 -*-
# /***************************************************************************
 # TrendMapperDialog
                                 # A QGIS plugin
 # calculate trendlines along catagories
                             # -------------------
        # begin                : 2018-07-28
        # git sha              : $Format:%H$
        # copyright            : (C) 2018 by Russell Loewe
        # email                : russloewe@gmai.com
 # ***************************************************************************/

# /***************************************************************************
 # *                                                                         *
 # *   This program is free software; you can redistribute it and/or modify  *
 # *   it under the terms of the GNU General Public License as published by  *
 # *   the Free Software Foundation; either version 2 of the License, or     *
 # *   (at your option) any later version.                                   *
 # *                                                                         *
 # ***************************************************************************/



from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication#, QPyNullVariant
from qgis.core import QgsMapLayerRegistry, QgsDataSourceURI, QgsFeatureRequest, QgsField, QgsVectorLayer, QgsFeature, QgsGeometry, QgsCoordinateReferenceSystem
from qgis.PyQt.QtCore import QVariant, QPyNullVariant
from datetime import datetime
# Initialize Qt resources from file resources.py
import os.path
from trend_mapper_logger import TrendMapperLogger
log = TrendMapperLogger()



def makeFeature(dstLayer, feature):
    '''Copy features form a source vector layer to a target layer. 
    Only copy features whos value of the keyCol attribute is in the 
    featureList array. When copying the features, only copy the 
    attributes whos name is in the attribute array.
    
    :param feature is actually a dict
    
    '''
    log.debug('makeFeature("{}", "{}")'\
                    .format(dstLayer, feature))
    dstFields = dstLayer.pendingFields()
    newFeature = QgsFeature()
    newFeature.setFields(dstFields)
    if 'GEOMETRY' not in feature:
        raise KeyError('No geometry in the supplied feature dict')
    newFeature.setGeometry(feature['GEOMETRY'])
    for name in feature:
        if name == 'GEOMETRY':
            continue
        newFeature[name] = feature[name]
    #for field in newFeature.fields():
       # name = str(field.name())
       # attrVal = feature[name]
       # newFeature[name] = attrVal
    return newFeature
        

def addResultFields(layer, result):
    ''' Add a float field in a layer for each dict key in results param
    
    :param layer: The layer to add new fields to
    :layer type: QgVectorLayer
    
    :param result: A dictionary of results from an analysis function
    :type result: dict
    
    :returns: nothing
    '''
    log.debug('call({},{})'.format(layer, result))
    checkTrue( layer.startEditing() )
    for i in result:
        checkTrue(layer.dataProvider().addAttributes([QgsField(i, 
                                         QVariant.Double)]))
    layer.updateFields()
    checkTrue(layer.commitChanges())
    
def createVectorLayer(srcLayer, newLayerName, fieldsToCopy):
    '''Create a new vector layer with geometry and selected fields 
    from a source vector layer
    
    :param srcLayer: The layer that we will be copying geometry and 
        fields from
    :type srcLayer: QgVectorLayer
    
    :param name: The name for the new vector layer
    :type name: str
    
    :param attributes: An array of attirbute names for which we will
        be copying the corresponding fields
    :type attributes: [str]
    
    :returns: The newly created vector layer
    :rtype: QgVectorLayer
    '''
    if newLayerName == '':
        newLayerName = "{}_new".format(str(srcLayer.name())) 
    log.debug('call("{}", "{}", "{}")'.format(srcLayer, newLayerName,
                                                        fieldsToCopy))
    srcFields = srcLayer.pendingFields()
    newFields = []
    #make a subset of the source layer fields
    for i in srcFields:
        if str(i.name()) in fieldsToCopy:
            newFields.append(i)
    #make sure 
    for name in fieldsToCopy:
        if name not in [str(i.name()) for i in newFields]:
            raise AttributeError('Field {} not in new layer'.format(name))
    #create a new point layer
    vl = QgsVectorLayer("Point?crs=epsg:27700", newLayerName, "memory")
    pr = vl.dataProvider()
    #add the subset of fields to the new layer
    checkTrue(vl.startEditing())
    checkTrue(pr.addAttributes(newFields))
    checkTrue(vl.commitChanges())
    return vl
    
def getUniqueKeys(layer, keyCol):
    '''Get the list of distinct values from an attribute column
    
    :param layer: The layer to pull the distinct values from.
    :type layer: QgVectorLayer
    
    :param keyCol: The name of the attribute column to pull the unique 
        values from.
    :type keyCol: str
    
    :returns: List of the distinct values found.
    :rtype: array
    '''
    log.debug('call("{}", "{}")'.format(layer, keyCol))
    idx = layer.fieldNameIndex(keyCol)
    if idx < 0:
        raise ValueError('Could not get field index for "{}" on {}'\
                            .format(keyCol, layer.name()))
    stations = layer.uniqueValues(idx)
    stations = map(str, stations) #convert all the entries to strings
    log.debug(':getUniqueKeys return: {}'.format(stations))
    return stations

def featureGenerator(layer, keyName, keyCol):
    '''Generate features from layer where keyCol equals keyName'''
    log.debug('featureGenerator({}, {}, {})'.format(str(layer.name()), 
                                                    keyName, keyCol))
    querry = "{} = '{}'".format(keyCol, keyName)
    featureIter = layer.getFeatures(QgsFeatureRequest().setFilterExpression(querry))
    return featureIter
        

def datapointGenerator(featureGenerator, attList):
    '''pull attributes in the attList from a feature and yield a dict'''
    log.debug("datapointGenerator({}, {})".format(featureGenerator,
                                                    attList))
    for feature in featureGenerator:
        result = {}
        for key in attList:
            result[key] = feature[key]
        result['GEOMETRY'] = feature.geometryAndOwnership() #using just .geometry() causes segfault down the line
        yield result

def filterDatapointGenerator(datapointGen, filterFun):
    '''only yield data points where filter fun is true'''
    log.debug("filterDatapointGenerator({}, {})".format( datapointGen, 
                                                  filterFun.__name__))
    for data in datapointGen:
        if filterFun(data):
            yield data

def convertedDatapointGenerator(datapointGen, convertFun, skipOnErr=True):
    '''Take stream of data points and apply a function to each then yield'''
    log.debug('mapDatapointGenerator({}, {})'.format(datapointGen, 
                                                convertFun.__name__))
    for data in datapointGen:
        try:
            dataOut = convertFun(data)
        except Exception as e:
            if skipOnErr:
                log.warning("Exception in converting data point: {}"\
                                .format(str(e)))
                continue
            else:
                raise e
        yield dataOut

def organizeData(datapointGen, dataAttr):
    '''collect data and organize data into x number of arrays'''
    log.debug("organizeData({}, {})".format(datapointGen, dataAttr))
    dataset = {}
    #make a dict of empty lists for each dataAttr
    for key in dataAttr:
        dataset[key] = []
    for data in datapointGen:
        for key in data:
            #collect all the dataAttr in a list
            if key in dataAttr:
                dataset[key].append(data[key])
            #copy the geometry blob and everything else one time
            elif key not in dataset:
                dataset[key] = data[key]
    return dataset
        
def getLayerByName(name):
    '''Find the layer object in the map registry by the string name
    
    :param name: The name of the layer to find.
    
    :returns: The layer object.
    :rtype: QgsVectorLayer
    '''
    log.debug('call("{}")'.format(name))
    layer=None
    for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
        if lyr.name() == name:
            return lyr
    raise AttributeError('Could not find layer: "{}"'.format(name))
            
def checkTrue(result):
    if  result == False:
        raise ValueError('Function returned False')
    elif result != True:
        raise ValueError('Function returned not True or False')
        
def mergeDicts(x, y, excluded=[]):
    for key in x:
        if key in y:
            raise KeyError('Conflicting dict keys')
    z = {}
    for key in x:
        if key not in excluded:
            z[key] = x[key]
    for key in y:
        if key not in excluded:
            z[key] = y[key]
    return z

def filterFun(point):
    for key in point:
        if type(point[key]) == QPyNullVariant:
            return False
    return True

def convFunNum(attr, dateColumn=None, dateFormat=None):
    if (dateColumn != None) and (dateFormat != None):
        def fun(point):
            for key in point:
                if key == dateColumn:
                    utime = datetime.strptime(point[key], dateFormat)
                    time = utime.toordinal()
                    point[key] = time
                elif key in attr:
                    point[key] = float(point[key])
                elif type(point[key]) != QgsGeometry:
                    point[key] = str(point[key])
            return point
    else:
        def fun(point):
            for key in point:
                if key in attr:
                    point[key] = float(point[key])
                elif type(point[key]) != QgsGeometry:
                    point[key] = str(point[key])
            return point
    return fun
