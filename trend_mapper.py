# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TrendMapper
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QPyNullVariant
from PyQt4.QtGui import QAction, QIcon
from PyQt4.QtSql import QSqlDatabase
from qgis.core import QgsMapLayerRegistry, QgsDataSourceURI, QgsFeatureRequest, QgsField, QgsVectorLayer, QgsFeature
from qgis.PyQt.QtCore import QVariant
# Initialize Qt resources from file resources.py
import resources
from analysis import calculateLinearRegression
# Import the code for the dialog
from trend_mapper_dialog import TrendMapperDialog
import os.path
import logging
LOGGER = logging.getLogger('QGIS')
FORMAT = '%(asctime)-15s:%(levelname)s: {}: %(message)s'.format(__name__)
logging.basicConfig(format=FORMAT, filename='{}.log'.format(__name__), level=logging.DEBUG)

class TrendMapper:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        loc = QSettings().value('locale/userLocale','en')
        locale = loc[0:2]

        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'TrendMapper_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&TrendMapper')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'TrendMapper')
        if self.toolbar == None:
            pass
        else:
            self.toolbar.setObjectName(u'TrendMapper')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('TrendMapper', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = TrendMapperDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/TrendMapper/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Compute rendlines for table catagorie.'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&TrendMapper'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def updateAttributeCombos(self):
        '''this is the callback function that gets called by the 
        dialoge class when it needs the attribute data for a layer 
        when the combo index is changed'''
        
        #grab the selected layer from the dialog class
        layerName = self.dlg.getInputLayer()
        if len(layerName) > 0:
            allLayers = self.iface.legendInterface().layers()
            allLayerNames = [lyr.name() for lyr in allLayers]
            layer_obj = allLayers[allLayerNames.index(layerName)]
            fields = layer_obj.pendingFields()
            self.dlg.setLayerAttributesCombos([field.name() for field in fields])
            
            
    def message(self, message):
        '''push a message to the status bar'''
        self.iface.messageBar().pushMessage('Info', message, level = Qgis.info)
        
    def run(self, test_run=False):
        """Run method that performs all the real work"""
        
        layers = self.iface.legendInterface().layers()
        allLayers = [layer for layer in layers if layer.type() == 0]
        self.dlg.setLayerInputCombo([layer.name() for layer in allLayers])
       #pass the callback function for updating combos
        if not test_run:
            self.dlg.setAttributeComboCallback(self.updateAttributeCombos)
            self.updateAttributeCombos()
        
        
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        if test_run:
            result = True
        else:
            result = self.dlg.exec_()
        # See if OK was pressed
        
        if result:
            logging.debug('runner called')
            # get all the data from the dialog
            inputLayerName = self.dlg.getInputLayer()
            keyCol = self.dlg.getCategoryCombo()
            xField = self.dlg.getXFieldCombo()
            yField = self.dlg.getYFieldCombo()
            outputLayerName = self.dlg.getOutputLayerName()
            logging.debug('''Trendmapper runner params:
                        inputLayerName: {}
                        keyCol: {}
                        xField: {}
                        yField: {}
                        outputLayerName: {}'''.format(
                        inputLayerName, keyCol, xField,
                        yField, outputLayerName))
                        
            #grab a reference to the input layer
            layer = getLayerByName(inputLayerName)
            
            #check that the x and y fields are numbers
            if getColType(layer, xField) in [7,10]:
                logging.error("Error: Field '{}' is a text column".format(xField))
                return
            elif getColType(layer, yField) in [7,10]:
                logging.error("Error: Field '{}' is a text column".format(yField))
                return
            
            newLayer = createVectorLayer(layer, outputLayerName, [keyCol, xField, yField])
            
            stations = getUniqueKeys(layer, keyCol)
            if len(stations) < 1:
                logging.error('No unique keys returned')
                raise ValueError('No unique keys returned')
            for st in stations:
                xData = getDataSet(layer, keyCol, st, xField)
                yData = getDataSet(layer, keyCol, st, yField)
               # self.message("{}   {}:{}  {}:{}".format(stations[0], xField, xData, yField, yData))
                result = calculateLinearRegression(zip(xData, yData))
                addResultFields(newLayer, result)
                copyFeatures(layer, newLayer, keyCol, stations, [keyCol, xField, yField])
                addResults(newLayer, keyCol, st, result)
            #self.message(str(result))

def copyFeatures(srcLayer, dstLayer, keyCol, featureList, attributes):
    '''Copy features form a source vector layer to a target layer. 
    Only copy features whos value of the keyCol attribute is in the 
    featureList array. When copying the features, only copy the 
    attributes whos name is in the attribute array.
    
    :param srcLayer: Layer that features are going to be copied from.
    :type srcLayer: QgVectorLayer
    
    :param dstLayer: Layer that features are going to be copied to
    :type dstLayer: QgVectorLayer
    
    :param keyCol: The name of the attribute field that we are 
        filtering our features by.
    :type keyCol: str
    
    :param featureList: An array of the names of the features that we
        are copying. Future feature: option of math expression
    :type featureList: [str]
    
    :param attributes: List of the attributes that we want copied 
        over with the feature.
    :type attributes: [str]
    
    :returns: nothing
    '''
    logging.debug('copyFeatures("{}", "{}", "{}", "{}", "{}")'\
                    .format(srcLayer, dstLayer, keyCol, featureList,
                            attributes))
    dstFields = dstLayer.pendingFields()
    newFeatures = []
    for name in featureList:
        querry = "{} = '{}'".format(keyCol, name)
        srcFeatures = srcLayer.getFeatures(QgsFeatureRequest().setFilterExpression(querry))
        for feature in srcFeatures:
            srcFeature = None
            #skip the feature if it does not have geometry attribute
            if feature.geometry() is not None: 
                srcFeature = feature
                break
            if srcFeature == None:
                raise AttributeError("Could not get geometry for: {}".format(name))
        newFeature = QgsFeature()
        newFeature.setFields(dstFields)
        newFeature.setGeometry(srcFeature.geometry())
        for attr in attributes:
            newFeature[attr] = srcFeature[attr]
        newFeatures.append(newFeature)
    if dstLayer.startEditing() == False:
        logging.error('Could not open {} for editing'.format(dstLayer.name()))
        raise AttributeError('Could not open {} for editing'.format(dstLayer.name()))
    dstLayer.addFeatures(newFeatures)
    dstLayer.commitChanges()
        
        
def addResults(layer, keyCol, keyName, results):
    '''Add the results values to the layer
    
    :param layer: Layer that results are added 
    :type layer: QgVectorLayer
    
    :param keyName: Name of feature to add results
    :type keyName: str
    
    :param keyCol: Field to match keyName
    :type keyCol: str
    
    :param results: Dict with result values and keys
    :param results: dict
    
    :returns: nothing
    '''
    logging.debug('addResults({}, {}, {}, {})'.format(layer, keyName, 
                                                    keyCol, results))
    querry = "{} = '{}'".format(keyCol, keyName)
    features = [f for f in layer.getFeatures(
                       QgsFeatureRequest().setFilterExpression(querry))]
    featureUpdates = {}
    
    if len(features) != 1:
        raise ValueError("not exactly 1 feature in return array")
    feature = features[0]
    for index in results:
        featureUpdates[feature.id()] = { index : results[index] }
    provider = layer.dataProvider()
    provider.changeAttributeValues( featureUpdates )


def addResultFields(layer, result):
    ''' Add a float field in a layer for each dict key in results param
    
    :param layer: The layer to add new fields to
    :layer type: QgVectorLayer
    
    :param result: A dictionary of results from an analysis function
    :type result: dict
    
    :returns: nothing
    '''
    logging.debug('addResultFields({},{}'.format(layer, result))
    if layer.startEditing() == False:
        raise AttributeError("Unable to start editing layer: {}"\
                                                 .format(layer.name()))
    for i in result:
        if layer.dataProvider().addAttributes([QgsField(i, 
                                         QVariant.Double)]) == False:
            raise AttributeError("Unable to add '{}' to layer: {}"\
                                              .format(i, layer.name()))
    if layer.updateFields() == False:
        raise AttributeError("Unable to update fields for layer: {}"\
                                                 .format(layer.name()))
    if layer.commitChanges() == False:
        raise AttributeError("Unable to commit changes to layer: {}"\
                                                 .format(layer.name()))
    
def createVectorLayer(srcLayer, name, attributes, addToCanvas=True):
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
    logging.debug('createVectorLayer("{}", "{}", "{}", addToCanvas={})'\
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
    if addToCanvas:
        QgsMapLayerRegistry.instance().addMapLayer(vl)
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
    logging.debug('getColType("{}", "{}")'.format(layer, keyCol))
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
    logging.debug('getUniqueKeys("{}", "{}")'.format(layer, keyCol))
    if int(layer.featureCount()) < 1:
        raise AttributeError('No features in layer: {}'.format(layer.name()))
    idx = layer.fieldNameIndex(keyCol)
    stations = layer.uniqueValues(idx)
    stations = map(str, stations) #convert all the entries to strings
    logging.debug(':getUniqueKeys return: {}'.format(stations))
    return stations

def getDataSet(layer, keyCol, keyName, field):
    '''Return all the values of an attirbute column for
    features matching keyName in the keyCol attribute
    
    :param layer: The layer to pull the data from
    :type layer: QgsVectorLayer
    
    :param keyCol: The attribute column that contians the name for 
        which we are filtering, example: 'STATION' 
    :type keyCol: str
    
    :param keyName: The name that we are looking to match in the 
        keyCol, example: 'US000PDX' 
    :type keyName: str
    
    :param field: The attribute column that we are pulling the data from
        example: 'TAVG' or 'DATE' 
    :type field: str
    '''
    logging.debug('getDataSet("{}", "{}", "{}", "{}")'.format(
                                    layer, keyCol, keyName, field))                                
    data = []
    querry = "{} = '{}'".format(keyCol, keyName)
    for feature in layer.getFeatures(QgsFeatureRequest().setFilterExpression(querry)):
        value = feature.attribute(field)
        if (type(value) is QPyNullVariant) :
            value = ''
        data.append(value)
    return data
    
def getLayerByName(name):
    '''Find the layer object in the map registry by the string name
    
    :param name: The name of the layer to find.
    
    :returns: The layer object.
    :rtype: QgsVectorLayer
    '''
    logging.debug('getLayerByName("{}")'.format(name))
    layer=None
    for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
        if lyr.name() == name:
            layer = lyr
            break
    return layer
            
            
            
def checkTrue(fun):
    def catcher(*args, **kargs):
        result = fun(*args, **kargs)
        if  result != True:
            raise ValueError('{} returned {}'.format(fun.__name__, result))
    return catcher
