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
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(TrendMapperDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.iface = iface
        self.InputLayerCombo.currentIndexChanged.connect(
                                        self.setLayerAttributesCombos)
        
    def getInputLayer(self):
        '''return vector layer from combo box for 
        analysis input
        returns string'''
        pass
        
    def getCatagoryCombo(self):
        '''get category choice from combo box,
        this is the unique values for regression analysis.
        returns string'''
        pass
        
    def getXFieldCombo(self):
        '''get data column name for independent variable
        for regression analysis
        returns string'''
        pass
        
    def getYFieldCombo(self):
        '''get data column for dependent variable in 
        regresison analysis
        returns string'''
        pass
        
    def getDiscardBadFitOption(self):
        '''get checkbox status from Discard Bad Fit box.
        returns boolean'''
        pass
        
    def getExportRisidualsOption(self):
        '''returns Export Riduals choice.
            returns boolean'''
        pass
        
    def getFilterOutliersOption(self):
        '''Get choice for filtering outliers check box.
        returns boolean'''
        pass
        
    def getThresholdValue(self):
        '''Gets the value for threshold input in regression
        analysis filter option. The number is the multiple of 
        standard deviations for outlier filter.
        returns float or int'''
        pass
        
    def getOutputLayerName(self):
        '''gets the name for the output layer from the 
        outputlayer line edit.
        returns string'''
        pass
        
    def setLayerInputCombo(self, layerlist):
        '''Get a list of available layers from 
        parent.'''
        pass

    def setLayerAttributesCombos(self):
        '''Updates the three combo boxes for catagory, x and y
        fields with the availbe attribute columns from selected
        layer. Called after selection has been made on InputVectorCombo.
         
         Note: this uses iface directly to get attribute list from
         layer. I would like to use dependency injection or something
         to try to remove this class's dependency on iface interface.'''
         pass
         
    def setAttributeComboCallback(self, callback_function):
        '''recieves a function to connect with the
         InputLayerCombo.currentIndexChanged connection. I'm
         doing this so that all iface stuff can be located in the
         main python file so that this class only has to pass and recieve
         data.'''
         pass
         
    def outputMessage(self, message):
        ''' Take text data from analysis output an display to 
        the user. Unsure as yet whether to us popup or messagebox on
        different tab with save option'''
        
        pass
