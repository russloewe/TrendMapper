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

from PyQt4 import QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'trend_mapper_dialog_base.ui'))


class TrendMapperDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(TrendMapperDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
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
         
    def setAttributeComboCallback(self, callback_function):
        '''recieves a function to connect with the
         InputLayerCombo.currentIndexChanged connection. I'm
         doing this so that all iface stuff can be located in the
         main python file so that this class only has to pass and recieve
         data.'''
        self.inputLayerCombo.currentIndexChanged.connect(
                                        callback_function)
