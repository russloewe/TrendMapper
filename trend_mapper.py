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
from trend_mapper_tools import *
# Import the code for the dialog
from trend_mapper_dialog import TrendMapperDialog
import os.path
#import the custom logger
from trend_mapper_logger import myLogger
log = myLogger()

import cProfile

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
        when the combo index is changed. This function is here and 
        not in the dialog class so that the dialog class doesn't 
        depend on the qgis interface.'''
        
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
            log.debug('runner called')
            # get all the data from the dialog
            inputLayerName = self.dlg.getInputLayer()
            keyCol = self.dlg.getCategoryCombo()
            xField = self.dlg.getXFieldCombo()
            yField = self.dlg.getYFieldCombo()
            outputLayerName = self.dlg.getOutputLayerName()
            copyAttr = self.dlg.getCopyAttrSelected()
            statsCheck = self.dlg.getExportRisidualsOption()
            formatXCol = self.dlg.getXDateFormatCheckbok()
            #need to add copy attributes
            log.debug('''Trendmapper runner params:
                        inputLayerName: {}
                        keyCol: {}
                        xField: {}
                        yField: {}
                        outputLayerName: {}'''.format(
                        inputLayerName, keyCol, xField,
                        yField, outputLayerName))
            
            #grab a reference to the input layer
            layer = getLayerByName(inputLayerName)
            dataAttr = [xField, yField]
            copyAttr.append(keyCol) #need to add way to get more from user
            stations = getUniqueKeys(layer, keyCol) #get the list of stations to process
            
            #create a function create a result feature for each station set
            def getdata(station):
                featureItr = featureGenerator(layer, station, keyCol)
                pointItr = datapointGenerator(featureItr, copyAttr + dataAttr)
                filterItr = filterDatapointGenerator(pointItr, filterFun)
                convItr = convertedDatapointGenerator(filterItr, 
                                           convFunNum(dataAttr),
                                           skipOnErr = True)
                data = organizeData(convItr, dataAttr)
                if (len(data[xField]) < 1) or (len(data[yField]) < 1):
                    return data, None
                else:
                    result = calculateLinearRegression(data[xField], 
                                                data[yField],
                                            includeStats = statsCheck)
                    return data, result
            #create the result layer
            newLayer = createVectorLayer(layer, outputLayerName, copyAttr)
            firstRun = True
            for station in stations:
                #get result for one station
                data, result = getdata(station)
                if result == None:
                    continue
                if firstRun:
                    #add the add the result attributes as fields in new layer
                    addResultFields(newLayer, result)
                    firstRun = False
                mergeResult = mergeDicts(data, result, excluded = dataAttr)
                newFeature = makeFeature(newLayer, mergeResult)
                checkTrue(newLayer.startEditing())
                newLayer.addFeatures([newFeature], makeSelected = False)
                checkTrue(newLayer.commitChanges())
            QgsMapLayerRegistry.instance().addMapLayer(newLayer)
