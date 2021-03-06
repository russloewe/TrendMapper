# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'russloewe@gmai.com'
__date__ = '2018-07-28'
__copyright__ = 'Copyright 2018, Russell Loewe'

import unittest
from qgis.core import *
from PyQt4.QtGui import QDialogButtonBox, QDialog
from test.utilities import get_qgis_app
from trend_mapper_dialog import TrendMapperDialog

from utilities import get_qgis_app
QGIS_APP = get_qgis_app()


class TrendMapperDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
        self.iface = IFACE
        self.dialog = TrendMapperDialog(self.iface)
        self.layer_yearly = QgsVectorLayer(
                                    './test/test_noaa_yearly.sqlite', 
                                    'test_noaa_yearly', 'ogr')
        self.layer_monthly = QgsVectorLayer(
                                    './test/test_noaa_monthly.sqlite',
                                     'test_noaa_monthly', 'ogr')
        QgsMapLayerRegistry.instance().addMapLayer(self.layer_yearly)
        QgsMapLayerRegistry.instance().addMapLayer(self.layer_monthly)
        
    def tearDown(self):
        """Runs after each test."""
        self.dialog = None
        self.layer_yearl = None
        self.layer_monthly = None

    def test_dialog_ok(self):
        """Test we can click OK."""

        button = self.dialog.button_box.button(QDialogButtonBox.Ok)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Accepted)
        
    def test_dialog_cancel(self):
        """Test we can click cancel."""
        button = self.dialog.button_box.button(QDialogButtonBox.Cancel)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Rejected)
        
    def test_setLayerAttributeCombos(self):
        '''test that we can update the three different layer 
        attribute combos'''
        testList = ['one', 'two', 'three']
        self.dialog.setLayerAttributesCombos(testList)
        for n in range(3):
            self.assertEqual(self.dialog.categoryCombo.findText(testList[n]) >= 0, True)
            self.assertEqual(self.dialog.xFieldCombo.findText(testList[n]) >= 0, True)
            self.assertEqual(self.dialog.yFieldCombo.findText(testList[n]) >= 0, True)
        testList2 = ['four', 'five', 'six']
        self.dialog.setLayerAttributesCombos(testList2)
        for n in range(3):
            self.assertEqual(self.dialog.categoryCombo.findText(testList[n]) < 0, True)
            self.assertEqual(self.dialog.xFieldCombo.findText(testList[n]) < 0, True)
            self.assertEqual(self.dialog.yFieldCombo.findText(testList[n]) < 0, True)

    def test_setLayerInputCombo(self):
        '''same test as the attribute combo test but for the layer
        input combo'''
        testList = ['test_noaa_yearly', 'test_noaa_monthly']
        self.dialog.setLayerInputCombo(testList)
        for n in range(2):
            self.assertEqual(self.dialog.inputLayerCombo.findText(testList[n]) >= 0, True)
        #testList2 = ['test_noaa_yearly', 'five', 'six']
        #self.dialog.setLayerInputCombo(testList2)
       # for n in range(3):
         #   self.assertEqual(self.dialog.inputLayerCombo.findText(testList[n]) < 0, True)

    def test_getInputCombo(self):
        '''test that the right layer is returned for the getInputLayer '''
        testList = ['test_noaa_yearly', 'test_noaa_monthly']
        self.dialog.setLayerInputCombo(testList)
        self.dialog.inputLayerCombo.setCurrentIndex(0) 
        self.assertEqual(self.dialog.getInputLayer(), 'test_noaa_yearly')
        self.dialog.inputLayerCombo.setCurrentIndex(1) 
        self.assertEqual(self.dialog.getInputLayer(), 'test_noaa_monthly')

        
    def test_checkboxGetters(self):
        '''test all of the checkbox getter functions'''
        self.dialog.exportRisidualsCheck.setChecked(True)
        self.dialog.dateCheck.setChecked(True)
        self.assertEqual(self.dialog.getExportRisidualsOption(), True)
        self.assertEqual(self.dialog.getDateFormatCheckbok(), True)
        self.dialog.exportRisidualsCheck.setChecked(False)
        self.dialog.dateCheck.setChecked(False)
        self.assertEqual(self.dialog.getExportRisidualsOption(), False)
        self.assertEqual(self.dialog.getDateFormatCheckbok(), False)
        
    def test_getOutputLayerName(self):
        '''check that the output layer name is correct'''
        self.dialog.outputLayerLine.setText('out.name')
        self.assertEqual(self.dialog.getOutputLayerName(), 'out.name')
        
    def test_comboGetters(self):
        '''test the three functions that get the attributes for analysisi'''
        self.dialog.setLayerAttributesCombos(['one', 'two', 'three', 
                                                'four'])
        self.dialog.categoryCombo.setCurrentIndex(0)
        self.dialog.xFieldCombo.setCurrentIndex(1)
        self.dialog.yFieldCombo.setCurrentIndex(2)
        self.dialog.dateFormatCombo.setCurrentIndex(3)
        self.assertEqual(self.dialog.getCategoryCombo(), 'one')
        self.assertEqual(self.dialog.getXFieldCombo(), 'two')
        self.assertEqual(self.dialog.getYFieldCombo(), 'three')
        self.assertEqual(self.dialog.getDateFormatCombo(), 'four')
        
    def test_Callback(self):
        '''test connection index change and updateAttributeCombo'''
        self.dialog.setLayerInputCombo(['test_noaa_monthly',
                                        'test_noaa_yearly'])
        self.dialog.inputLayerCombo.setCurrentIndex(0)
        result1 = self.dialog.categoryCombo.count()
        self.dialog.inputLayerCombo.setCurrentIndex(1)
        result2 = self.dialog.categoryCombo.count()
        self.assertEqual(result1, 9)
        self.assertEqual(result2, 10)
    

if __name__ == "__main__":
    suite = unittest.makeSuite(TrendMapperDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
