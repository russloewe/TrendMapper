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
                  QgsField('dataDouble', QVariant.Double),
                  QgsField('dataInt', QVariant.Int), 
                  QgsField('dataStr', QVariant.String),
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
        #create 50 test features for the test
        for i in range(50):
            #create feature with fields from parent layer
            feature = QgsFeature()
            feature.setFields(vl.fields())
            #create a random geometry point in lat/lon domain
            x = random.uniform(-180, 180)
            y = random.uniform(-90, 90)
            layerPoint = transf.transform(QgsPoint(x, y))
            feature.setGeometry(QgsGeometry.fromPoint(layerPoint))
            #give feature one of four names
            if i%4 == 0:
                #first feature has all valid values with str ints
                feature['name'] = 'one'
                feature['dataDouble'] = random.uniform(-100, 100)
                feature['dataInt'] = random.randint(0,100)
                feature['dataStr'] = "{}".format(random.randint(0,100))
            elif i%4 == 1:
                #second feature has all valid values with str float
                feature['name'] = 'two'
                feature['dataDouble'] = random.uniform(-100, 100)
                feature['dataInt'] = random.randint(0,100)
                feature['dataStr'] = "{}".format(random.uniform(0,100))
            elif i%4 == 2:
                #third feature will have sporadic gaps
                feature['name'] = 'three'
                if random.randint(0, 3) == 0:
                    feature['dataDouble'] = ''
                else:
                    feature['dataDouble'] = random.uniform(-100, 100)
                if random.randint(0, 3) == 0:
                    feature['dataInt'] = ''
                else:
                    feature['dataInt'] = random.randint(0,100)
                if random.randint(0, 3):
                    feature['dataStr'] = "{}".format(random.uniform(0,100))
                else:
                    feature['dataStr'] = "text"
            else:
                #fourth will have no data for double and str colum
                feature['name'] = 'four'
                feature['dataDouble'] = ''
                feature['dataInt'] = random.randint(0,100)
                feature['dataStr'] = ''
            features.append(feature)        
        #add the feature to the canvas
        checkTrue(vl.startEditing())
        vl.dataProvider().addFeatures(features)
        checkTrue(vl.commitChanges())
        QgsMapLayerRegistry.instance().addMapLayer(vl)
        self.layer = vl
        
        #set the category combo to the name field
        self.trendmapper.dlg.getCategoryCombo = lambda : 'name'
        
            
        
        

    def tearDown(self):
        """Runs after each test."""
        self.trendmapper.dlg = None
        self.trendmapper = None

    
    def test_dialoge(self):
        '''Test that the dialoge box loaded'''
        self.assertTrue(self.trendmapper.dlg is not None)

    def test_run_intdouble(self):
        '''Test that the run function works for int and float'''
        #set the xField combo
        self.trendmapper.dlg.getXFieldCombo = lambda : 'dataInt'
        #set the yField combo
        self.trendmapper.dlg.getYFieldCombo = lambda : 'dataDouble'
        self.trendmapper.run(test_run = True)
    
    def test_run_intst(self):
        '''Test that the run function works for int and str num'''
        #set the xField combo
        self.trendmapper.dlg.getXFieldCombo = lambda : 'dataInt'
        #set the yField combo
        self.trendmapper.dlg.getYFieldCombo = lambda : 'datastr'
        self.trendmapper.run(test_run = True)
    
    def test_run_strstr(self):
        '''Test that the run function works for non numerical'''
        #set the xField combo
        self.trendmapper.dlg.getXFieldCombo = lambda : 'name'
        #set the yField combo
        self.trendmapper.dlg.getYFieldCombo = lambda : 'name'
        self.trendmapper.run(test_run = True)
  
if __name__ == "__main__":
    suite = unittest.makeSuite(TrendMapperTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
