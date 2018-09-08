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

from PyQt4.QtGui import QDialogButtonBox, QDialog
from test.utilities import get_qgis_app
from trend_mapper import TrendMapper
from qgis.core import *
from qgis.PyQt.QtCore import QVariant
import random

#from utilities import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
from tools import checkTrue
import sys

def trace(frame, event, arg):
    print "%s, %s:%d" % (event, frame.f_code.co_filename, frame.f_lineno)
    return trace

import faulthandler
faulthandler.enable()

#sys.settrace(trace)


class TrendMapperTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.trendmapper = TrendMapper(IFACE)
        self.trendmapper.add_action('icon.png', 'test', self.trendmapper.run,
                    add_to_menu = False, add_to_toolbar = None)
        
        #define the test fields
        fields = [QgsField('LONGITUDE', QVariant.Double), 
                  QgsField('LATITUDE', QVariant.Double),
                  QgsField('data1', QVariant.Double),
                  QgsField('data2', QVariant.Int), 
                  QgsField('name', QVariant.String)   ]
        #create a test layer
        vl = QgsVectorLayer("Point", 'test', "memory")
        pr  = vl.dataProvider()
        checkTrue(vl.startEditing()) 
        pr.addAttributes( fields )
        checkTrue(vl.commitChanges())
        #create a set of features
        transf = QgsCoordinateTransform(QgsCoordinateReferenceSystem(4326), QgsCoordinateReferenceSystem(32612))
        features = []
        for i in range(50):
            x = random.uniform(-180, 180)
            y = random.uniform(-90, 90)
            feature = QgsFeature()
            feature.setFields(vl.fields())
            layerPoint = transf.transform(QgsPoint(x, y))
            feature.setGeometry(QgsGeometry.fromPoint(layerPoint))
            if i%4 == 0:
                name = 'one'
            elif i%4 == 1:
                name = 'two'
            elif i%4 == 3:
                name = 'three'
            else:
                name = 'four'
            feature['name'] = name
            if random.randint(0,100)%5 == 0:
                feature['data1'] = None
            elif random.randint(0,100)%5 == 0:
                feature['data1'] = ''
            else:
                feature['data1'] = random.uniform(-100, 100)
            feature['data2'] = random.randint(0,100)
            features.append(feature)
        #add the feature to the canvas
        checkTrue(vl.startEditing())
        vl.dataProvider().addFeatures(features)
        checkTrue(vl.commitChanges())
        QgsMapLayerRegistry.instance().addMapLayer(vl)
        
        #set the category combo to the name field
        self.trendmapper.dlg.getCategoryCombo = lambda : 'name'
        #set the xField combo
        self.trendmapper.dlg.getXFieldCombo = lambda : 'data1'
        #set the yField combo
        self.trendmapper.dlg.getYFieldCombo = lambda : 'data2'
            
        self.layer = vl
        
        

    def tearDown(self):
        """Runs after each test."""
        self.trendmapper.dlg = None
        self.trendmapper = None

    
    def test_dialoge(self):
        '''Test that the dialoge box loaded'''
        self.assertTrue(self.trendmapper.dlg is not None)

    def test_run(self):
        '''Test that the run function works'''
        self.trendmapper.run(test_run = True)
  
if __name__ == "__main__":
    suite = unittest.makeSuite(TrendMapperTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
