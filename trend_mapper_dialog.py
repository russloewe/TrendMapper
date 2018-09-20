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

import os 
from PyQt4 import QtGui, uic, QtCore

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'trend_mapper_dialog_base.ui'))


class TrendMapperDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(TrendMapperDialog, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
            
    def getInputLayer(self):
        '''return vector layer from combo box for 
        analysis input
        returns string'''
        return(str(self.inputLayerCombo.currentText()))
        
    def getCategoryCombo(self):
        '''get category choice from combo box,
        this is the unique values for regression analysis.
        returns string'''
        return(str(self.categoryCombo.currentText()))
        
        
    def getXFieldCombo(self):
        '''get data column name for independent variable
        for regression analysis
        returns string'''
        return(str(self.xFieldCombo.currentText()))
        
    def getYFieldCombo(self):
        '''get data column for conversion
        returns string'''
        return(str(self.yFieldCombo.currentText()))
    
    def getDateFormatCombo(self):
        '''get data column for dependent variable in 
        regresison analysis
        returns string'''
        return(str(self.dateFormatCombo.currentText()))
        
    def getDateFormatCheckbok(self):
        '''get status from the date format checkbox'''
        return(self.dateCheck.isChecked())
        
    def getExportRisidualsOption(self):
        '''returns Export Riduals choice.
            returns boolean'''
        return(self.exportRisidualsCheck.isChecked())
    
    def getDateFormatText(self):
        '''gets the name for the output layer from the 
        outputlayer line edit.
        returns string'''
        return(self.dateFormatLineEdit.text())
        
    def getOutputLayerName(self):
        '''gets the name for the output layer from the 
        outputlayer line edit.
        returns string'''
        return(self.outputLayerLine.text())
    
    def getCopyAttrSelected(self):
        '''Get a list of the attributes selected in the copy
        attr QListWidget'''
        return [item.text() for item in self.copyAttr.selectedItems()]
        
    def setLayerInputCombo(self, layerList):
        '''Get a list of available layers from 
        parent.'''
        self.inputLayerCombo.clear()
        for item in layerList:
            self.inputLayerCombo.addItem(item)

    def setLayerAttributesCombos(self, inputList):
        '''Updates the three combo boxes for catagory, x and y
        fields with the availbe attribute columns from selected
        layer. Called after selection has been made on InputVectorCombo.
        '''
        self.categoryCombo.clear()
        self.xFieldCombo.clear()
        self.yFieldCombo.clear()
        self.copyAttr.clear()
        self.dateFormatCombo.clear()
        for item in inputList:
            self.categoryCombo.addItem(item)
            self.xFieldCombo.addItem(item)
            self.yFieldCombo.addItem(item)
            self.copyAttr.addItem(item)
            self.dateFormatCombo.addItem(item)
         
    def updateAttributeCombos(self):
        '''this is the callback function that gets called by the 
        dialoge class when it needs the attribute data for a layer 
        when the combo index is changed. This function is here and 
        not in the dialog class so that the dialog class doesn't 
        depend on the qgis interface.'''
        layerName = self.getInputLayer()
        if len(layerName) > 0:
            allLayers = self.iface.legendInterface().layers()
            allLayerNames = [lyr.name() for lyr in allLayers]
            layer_obj = allLayers[allLayerNames.index(layerName)]
            fields = layer_obj.pendingFields()
            self.setLayerAttributesCombos([field.name() for field in fields])
            
    def message(self, message):
        '''push a message to the status bar'''
        self.iface.messageBar().pushMessage('Info', message)
        
    def setProgressBar(self, main, text, maxVal=100):
        '''Create a message bar widget, add a progress bar and abort
        button. Add the widget to the message bar and hide the X, exit
        button.
        '''
        self.prgrunning = True
        self.prgWidget = self.iface.messageBar().createMessage(main, text)
        self.prgBar = QtGui.QProgressBar()
        self.prgBar.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.prgBar.setValue(0)
        self.prgBar.setMaximum(maxVal)
        self.abortButton = QtGui.QPushButton('Abort', self)
        self.prgWidget.layout().addWidget(self.abortButton)
        self.prgWidget.layout().addWidget(self.prgBar)
        self.iface.messageBar().pushWidget(self.prgWidget,
                                           self.iface.messageBar().INFO)
        self.iface.messageBar().findChildren(QtGui.QToolButton)[0].setHidden(True)
                                           
    def ProgressBar(self, value, msg):
        '''Update the progressbar. Takes a number and a message'''
        if self.prgrunning:
            if (value >= self.prgBar.maximum()):
                self.ProgressBarClose()
            else:
                self.prgBar.setValue(value)
                self.prgWidget.setText(msg)

    def ProgressBarClose(self):
        '''This method closes the progress bar widget'''
        self.prgrunning = False
        self.iface.messageBar().findChildren(QtGui.QToolButton)[0].setHidden(False)
        self.iface.messageBar().clearWidgets()
        self.iface.mapCanvas().refresh()
