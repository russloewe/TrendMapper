# -*- coding: utf-8 -*-
# /***************************************************************************
 # TrendMapperTools
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



from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from qgis.PyQt.QtCore import QVariant, QPyNullVariant
from qgis.core import QgsMapLayerRegistry, QgsDataSourceURI 
from qgis.core import QgsFeatureRequest, QgsField, QgsVectorLayer, QgsFeature
from qgis.core import QgsGeometry, QgsCoordinateReferenceSystem
from datetime import datetime
from trend_mapper_log import TrendMapperLogger
# Initialize Qt resources from file resources.py
import os.path
# Set the logger
log = TrendMapperLogger()



def makeFeature(dstLayer, newFeatureDict):
    '''
    Copy features form a source vector layer to a target layer. 
    Only copy features whos value of the keyCol attribute is in the 
    featureList array. When copying the features, only copy the 
    attributes whos name is in the attribute array.
    
    :param dstLayer: The layer for which the new feature's fields will be 
        taken from.
    :type dstLayer: QgsVectorLayer
    
    :param newFeatureDict: Dictionary with the attributes to be assigned 
        to the new feature. Dictionary keys are the string name for the field.
    :type newFeatureDict: Dict
    
    :return: The new feature object.
    :rtype: QgsFeature
    
    .. todo:: See if QFeature has method for adding attributes from a dict.
    
    '''
    # Set the fields for the new feature from the dst layer
    dstFields = dstLayer.pendingFields()
    newFeature = QgsFeature()
    newFeature.setFields(dstFields)
    # Verify the input dict has all the fields and warn if not
    for fieldname in [str(f.name()) for f in dstFields]:
        if fieldname not in newFeatureDict:
            log.warn("{} missing from input feature dict")
    # Geometry is assigned differently than other attributes
    newFeature.setGeometry(newFeatureDict['GEOMETRY'])
    # Copy attr to new feature object
    for name in newFeatureDict:
        if name == 'GEOMETRY':
            continue
        newFeature[name] = newFeatureDict[name]
    return newFeature
        
def addResultFields(dstLayer, resultDict):
    ''' Add a QgsField of type double float type for each key in the
        resultDict.
    
    :param dstLayer: The layer to add new fields.
    :type dstLayer: QgVectorLayer
    
    :param resultDict: A dictionary containing the results from an analysis 
        function. All entries in the resultDict are assumed to be ints or 
        floats.
    :type resultDict: dict
    
    :returns: nothing
    '''
    newFields = []
    for key in resultDict:
        newFields.append(QgsField(key, QVariant.Double))
    checkTrue( dstLayer.startEditing() )
    checkTrue(dstLayer.dataProvider().addAttributes(newFields))
    dstLayer.updateFields()
    checkTrue(dstLayer.commitChanges())
    
def createVectorLayer(srcLayer, newLayerName, fieldsToCopy, crs='epsg:27700'):
    '''Create a new vector layer with geometry and selected fields 
    from a source vector layer.
    
    :param srcLayer: The layer that we will be copying geometry and 
        fields from.
    :type srcLayer: QgVectorLayer
    
    :param newLayerName: The name for the new vector layer.
    :type newLayerName: str
    
    :param fieldsToCopy: An array of attirbute names for which we will
        be copying the corresponding fields.
    :type fieldsToCopy: [str]
    
    :param crs: The crs for the new layer. Defaults to "epsg:27700".
    :type crs: str
    
    :returns: The newly created vector layer.
    :rtype: QgVectorLayer
    
    .. todo:: Option to automatically copy crs from source layer.
    '''
    if (newLayerName == '') or (newLayerName is None):
        log.error('Invalid name for new layer: "{}"'.format(newLayerName))
        raise ValueError('Invalid layer name: "{}"'.format(newLayerName)) 
    srcFields = srcLayer.pendingFields()
    # Make a list of srcField names
    fieldName = lambda x : str(x.name())
    srcFieldNames = map(fieldName, srcFields)
    # Filter out fields that arent in fieldsToCopy
    ifIn = lambda x : True if fieldName(x) in fieldsToCopy else False 
    newFields = filter(ifIn, srcFields)
    # Check that all the fields we wanted were copied
    ifIn = lambda x : False if x in srcFieldNames else True
    leftOverFields = filter(ifIn, fieldsToCopy)
    if len(leftOverFields) != 0:
        log.error('Fields "{}" not copied to new layer.'\
                                                     .format(leftOverFields))
        raise AttributeError('Fields "{}" not copied to new layer.'\
                                                     .format(leftOverFields))
    #create a new point layer in memory
    vl = QgsVectorLayer("Point?crs={}".format(crs), newLayerName, "memory")
    pr = vl.dataProvider()
    #add the subset of fields to the new layer
    checkTrue(vl.startEditing())
    checkTrue(pr.addAttributes(newFields))
    checkTrue(vl.commitChanges())
    return vl
    
def getUniqueKeys(srcLayer, keyCol):
    '''Get the list of distinct values from an attribute column
    
    :param srcLayer: The layer to pull the distinct values from.
    :type srcLayer: QgVectorLayer
    
    :param keyCol: The name of the attribute column to pull the unique 
        values from.
    :type keyCol: str
    
    :returns: List of the distinct values found as strings.
    :rtype: [str]
    '''
    idx = srcLayer.fieldNameIndex(keyCol)
    if idx < 0:
        log.error('Cant get unique values for column "{}"'.format(keyCol))
        raise ValueError('Could not get field index for "{}" on {}'\
                            .format(keyCol, srcLayer.name()))
    stations = srcLayer.uniqueValues(idx)
    stations = map(str, stations) 
    return stations

def featureGenerator(srcLayer, keyName, keyCol):
    '''Make a filtered QgsFeatureIterator so features with attribute "keyName"
    in column "keyCol" are returned.
    
    :param srcLayer: The layer to get features from.
    :type srcLayer: QgsVectorLayer
    
    :param keyName: The attribute value to filter features by.
    :type keyName: str
    
    :param keyCol: The name of the feature field to match keyName against.
    :type keyCol: str
    
    :return: A filterd feature iterator
    :rtype: QgsFeatureiterator
    '''
    querry = "{} = '{}'".format(keyCol, keyName)
    featureIter = srcLayer.getFeatures(QgsFeatureRequest().setFilterExpression(querry))
    return featureIter
        

def datapointGenerator(featureGenerator, attList):
    '''Make a generator that takes features from a feature iterator object
    and yields datapoints as a dict for  the desired attributes given in 
    attList.
    
    :param featureGenerator: The feature souce.
    :type featureGenerator: QgsFeatureIterator
    
    :param attList: A list of attribute fields we want to extract.
    :type attList: [str]
    
    :return: A datapoint iterator.
    :rtype: generator object
    '''
    for feature in featureGenerator:
        result = {}
        for key in attList:
            result[key] = feature[key]
        # Using .geometry() causes segfault down the line
        result['GEOMETRY'] = feature.geometryAndOwnership() 
        yield result

def filterDatapointGenerator(datapointGen, filterFun):
    '''Makes a generator that filters the output from a datapointGenertor
    using the supplied function: filterFun. If filterFun(datapoint) returns
    True the datapoint is yielded, and if it returns False the datapoint is
    skipped.
    
    :param datapointGen: A generator object produced from the 
        datapointGenerator() function.
    :type datapointGen: generator object
    
    :param filterFun: A function that takes a dict and returns a bool.
    :type filterFun: function
    
    :return: A filtered datapoint generator.
    :rtype: generator object
    '''
    for data in datapointGen:
        if filterFun(data):
            yield data

def convertedDatapointGenerator(datapointGen, convertFun, skipOnErr=True):
    '''Makes a generator that converts the output from a datapoint
    generator using the supplied function: convertFun.
    
    :param datapointGen: A generator object produced from the 
        datapointGenerator() function.
    :type datapointGen: generator object
    
    :param convertFun: A function that takes a dict and returns a dict.
    :type convertFun: function
    
    :param skipOnErr: Flag, if True skip when convertFun raises an 
        exception and pass a warning to the logger. If false, raise 
        an exception. Default to True.
    :type skipOnErr: bool
    
    :return: Datapoint generator.
    :rtype: generator object
    '''
    for data in datapointGen:
        try:
            dataOut = convertFun(data)
        except Exception as e:
            if skipOnErr:
                log.warn('Exception converting datapoint {}: {}.'\
                                            .format(data, e))
                continue
            else:
                raise Exception('Exception converting datapoint {}: {}.'\
                                            .format(data, e))
        yield dataOut

def organizeData(datapointGen, dataAttr):
    '''Collect the data from a datapoint generator and organize all the 
    points from the datapoint generator into one dict. The attributes for the
    datapoints that are in dataAttr are organized as lists and the rest are 
    only retrived from the first datapoint.
    
    :param datapointGen: A generator object produced from the 
        datapointGenerator() function.
    :type datapointGen: generator object
    
    :param dataAttr: A list of the attributes that are to be collected as 
        lists.
    :type dataAttr: [str]
    
    :return: A dataset organized into a dict.
    :rtype: dict
    '''
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
