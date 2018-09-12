from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QPyNullVariant
from qgis.core import QgsMapLayerRegistry, QgsDataSourceURI, QgsFeatureRequest, QgsField, QgsVectorLayer, QgsFeature
from qgis.PyQt.QtCore import QVariant
# Initialize Qt resources from file resources.py
import os.path
from trend_mapper_logger import myLogger
log = myLogger(myLogger.INFO)



def addFeatures(dstLayer, featureSource):
    '''Copy features form a source vector layer to a target layer. 
    Only copy features whos value of the keyCol attribute is in the 
    featureList array. When copying the features, only copy the 
    attributes whos name is in the attribute array.
    
    '''
    log.debug('call("{}", "{}")'\
                    .format(dstLayer, featureSource))
    dstFields = dstLayer.pendingFields()
    newFeatures = []
    for featureIter, resultDict in featureSource:
        try:
            feature = featureIter.next()
        except StopIteration:
            log.warning("No features in feature iterator")
            continue
        newFeature = QgsFeature()
        newFeature.setFields(dstFields)
        newFeature.setGeometry(feature.geometry())
        for field in newFeature.fields():
            name = field.name()
            if name in resultDict:
                newFeature[name] = resultDict[name]
            else:
                newFeature[name] = feature[name]
        newFeatures.append(newFeature)
    checkTrue(dstLayer.startEditing())
    dstLayer.addFeatures(newFeatures)
    checkTrue(dstLayer.commitChanges())
        

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
    #print 'Result: {}'.format(result)
    for i in result:
        if type(i) != str:
            log.error('Fieldname paramater: "{}" is not a str'.format(i))
            raise TypeError('Fieldname paramater: "{}" is not a str'.format(i))
        checkTrue(layer.dataProvider().addAttributes([QgsField(i, 
                                         QVariant.Double)]))
    checkTrue(layer.updateFields())
    checkTrue(layer.commitChanges())
    
def createVectorLayer(srcLayer, name, attributes, addToCanvas=False):
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
    
    :param addToCanvas: Optional flag to add the new layer to the 
        qgis canvas map registry
    :type addToCanvas: bool
    
    :returns: The newly created vector layer
    :rtype: QgVectorLayer
    '''
    if name == '':
        name = "{}_new".format(str(srcLayer.name())) 
    log.debug('call("{}", "{}", "{}", addToCanvas={})'\
                    .format(srcLayer, name, attributes, addToCanvas))
    fields = srcLayer.pendingFields()
    newFields = []
    #make a subset of the source layer fields
    for i in fields:
        if str(i.name()) in attributes:
            newFields.append(i)
    #create a new point layer
    vl = QgsVectorLayer("Point", name, "memory")
    pr = vl.dataProvider()
    #add the subset of fields to the new layer
    if vl.startEditing() == False:
        raise AttributeError("Unable to start editing layer: {}"\
                                                 .format(vl.name()))
    pr.addAttributes( newFields )
    if vl.commitChanges() == False:
        raise AttributeError("Unable to commit changes to layer: {}"\
                                                 .format(vl.name()))
    return vl
    
    
def getColType(layer, keyCol):
    ''' Get the type for an attribute column in a layer. Just returns
    the integer representation. Use to quickly check if a field is 
    numeric or text, values in [7,10] are text.
    
    :param layer: The layer containing the column to check
    :type layer: QgVectorLayer
    
    :param keyCol: The name of the column to check
    :type keyCol: str
    
    :returns: The integer represention of the column type
    :rtype: int
    '''
    log.debug('call("{}", "{}")'.format(layer, keyCol))
    fields = layer.pendingFields()
    for i in fields:
        if str(i.name()) == keyCol:
            return i.type()
    return None
    
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
    if int(layer.featureCount()) < 1:
        raise AttributeError('No features in layer: {}'.format(layer.name()))
    idx = layer.fieldNameIndex(keyCol)
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
        result['GEOMETRY' : feature.getGeometry()]
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

def organizeData(datapointGen):
    '''organize data into x number of arrays'''
    pass
    
def getData(srcLayer, keyCol, dataCols):
    ''' An iterator that returns the dataset for a 'station',aka unique
    key on each iteration along with an iterator that generates the
    features corresponding to the data set
    
    :param srcLayer: Layer to querry data from.
    :type srcLayer: QgsVectorLayer
    
    :param keyCol: Name of attribute field that data is grouped by
    :type keyCol: str
    
    :param dataCols: Array of the names of attribute fields to pull 
        values from. Aribtrary length.
    :type dataCols: [str, str, ...]
    
    :returns: A tuple contianing two elements. First element it a new 
        instance of the iterator used to querry features data was pulled,
        second is an array of tuples. Each tuple contains a value for
        each of the data fields provided in :param dataCols: in the 
        same order.
    :rtype: (QgsFeatureIter, [(float, float, ...), ...])'''
    log.debug('call("{}", "{}", {}'.format(srcLayer, keyCol, dataCols))
    for keyName in getUniqueKeys(srcLayer, keyCol):
        log.debug('keyName: {}'.format(keyName))
        data = []
        querry = "{} = '{}'".format(keyCol, keyName)
        featureIter = srcLayer.getFeatures(QgsFeatureRequest().setFilterExpression(querry))
        for feature in featureIter:
            point = []
            for col in dataCols:
                try:
                    val = float(feature[col])
                except (ValueError, TypeError):
                    val = ''
                point.append(val)
            point = tuple(point)
            data.append(point)
        if len(data) < 1:
            log.error('No data in dataset')
           # raise ValueError('No data in dataset')
        newFeatureIter =  srcLayer.getFeatures(QgsFeatureRequest().setFilterExpression(querry))
        yield (newFeatureIter, data) 
        
def analyze(function, dataIter):
    '''Create an iterator that gives analyzed data and feateru iterator
    
    :param function: The function to apply to the dataset
    :type function: function
    
    :param dataIter: An iterator that returns a list of data points 
        and the function iterator
    :type dataIter: generator object
    
    :returns: iterator object
    '''
    log.debug('call(funcName: {}, {})'.format(function.__name__, dataIter))
    for item in dataIter:
        featureIter, dataset = item
        #filter out data points like (1, '') or (1, )
        dataset = filter(isNum, dataset)
        #skip empty datasets
        if len(dataset) < 1:
            log.warning('No data returned from data iterator')
            continue
        else:
            result = function(dataset)
            yield (featureIter, result)
    
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
            layer = lyr
            break
    return layer
            
def isNum(x):
    '''Return true if each element of x is float or integer'''
    for i in x:
        if (type(i) != int) and (type(i) != float):
            return False
    return True
            
def checkTrue(fun):
    def catcher(*args, **kargs):
        result = fun(*args, **kargs)
        if  result != True:
            raise ValueError('{} returned {}'.format(fun.__name__, result))
    return catcher

def merge_two_dicts(x, y):
    z = x.copy()  
    z.update(y)   
    return z

def splitDict(dic, keys):
    '''split a dictionary return both, with keys in first'''
    dic1 = {}
    dic2 = {}
    for k in dic:
        if k in keys:
            dic1[key] = dic[key]
        else:
            dic2[key] = dic[key]
    return dic1, dic2
