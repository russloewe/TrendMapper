# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TrendMapper
                                 A QGIS plugin
 calculate trendlines along catagories
                              -------------------
        begin                : 2018-07-28
        git sha              : '$Format:%H$'
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
import os.path
from qgis.core import QgsMapLayerRegistry, QgsMessageLog
from PyQt4 import QtGui, uic, QtCore
# Initialize Qt resources from file resources.py
import resources
# Import TrendMapper resources
from analysis import calculateLinearRegression
from trend_mapper_dialog import TrendMapperDialog
from trend_mapper_process import TrendMapperProcess
from trend_mapper_logger import TrendMapperLogger
from trend_mapper_tools import getLayerByName, getUniqueKeys, createVectorLayer
# Set the logger
log = QgsMessageLog.logMessage
INFO = 0
WARNING = 1
CRITICAL = 2

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
        loc = QtCore.QSettings().value('locale/userLocale', 'en')
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
        if self.toolbar is None:
            pass
        else:
            self.toolbar.setObjectName(u'TrendMapper')
        self.totalCounter = 1
        self.counter = 0

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
        return QtCore.QCoreApplication.translate('TrendMapper', message)

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
        self.dlg = TrendMapperDialog(self.iface)

        icon = QtGui.QIcon(icon_path)
        action = QtGui.QAction(icon, text, parent)
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

    def stp(self):
        '''Add the new layer to the canvas when the processing
        thread signals it's done
        '''
        QgsMapLayerRegistry.instance().addMapLayer(self.newLayer)

    def run(self, test_run=False):
        """Run method when TrendMapper in launched.
        Sets up and shows dialog and launches TrendMapper.process()
        """

        # Give the dialoge the list of layers
        layers = self.iface.legendInterface().layers()
        allLayers = [layer for layer in layers if layer.type() == 0]
        self.dlg.setLayerInputCombo([layer.name() for layer in allLayers])
        self.dlg.updateAttributeCombos()
        if test_run:
            result = True
        else:
            # show the dialog
            self.dlg.show()
            # Run the dialog event loop
            result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            self.process()

    def process(self):
        '''This is where a lot of the work is done. All the values
        from the dialog are retrieved, then the TrendMapperProcess
        worker thread and the progress bar are set up, connected
        and then launched'''
        # get all the data from the dialog
        inputLayerName = self.dlg.getInputLayer()
        keyCol = self.dlg.getCategoryCombo()
        xField = self.dlg.getXFieldCombo()
        yField = self.dlg.getYFieldCombo()
        outputLayerName = self.dlg.getOutputLayerName()
        copyAttr = self.dlg.getCopyAttrSelected()
        statsCheck = self.dlg.getExportRisidualsOption()
        formatDateCol = self.dlg.getDateFormatCheckbok()
        dateCol = self.dlg.getDateFormatCombo()
        dateFormat = self.dlg.getDateFormatText()
        # start progressbar
        self.dlg.setProgressBar('TrendMapper', '')
        # set up the rest of the paramters for the worker thread
        layer = getLayerByName(inputLayerName)
        copyAttr.append(keyCol)
        self.dlg.ProgressBar(0,
                         'Finding unique entries in {}'.format(keyCol))
        stations = getUniqueKeys(layer, keyCol)
        # create the new layer
        self.newLayer = createVectorLayer(layer, outputLayerName,
                                          copyAttr)
        # set up the worker thread
        tmprocess = TrendMapperProcess(self.newLayer, stations, xField,
                                       yField, copyAttr)
        tmprocess.createConvFunction(formatDateCol, dateCol, dateFormat)
        tmprocess.createDataFunction(layer, keyCol, statsCheck)
        # set up thread signal slots
        self.dlg.connect(tmprocess, tmprocess.progSig,
                         self.dlg.ProgressBar)
        self.dlg.connect(tmprocess, tmprocess.stopSig, self.stp)
        self.dlg.connect(tmprocess, tmprocess.msgSig, self.dlg.message)
        self.dlg.connect(tmprocess, tmprocess.abortSig,
                         self.dlg.ProgressBarClose)
        self.dlg.abortButton.clicked.connect(tmprocess.abort)
        # start the worker thread
        tmprocess.start()
