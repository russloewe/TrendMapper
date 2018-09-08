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
from qgis.core import *
from qgis.PyQt.QtCore import QVariant
import random
from trend_mapper_tools import *

#from utilities import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

import sys

def trace(frame, event, arg):
    print "%s, %s:%d" % (event, frame.f_code.co_filename, frame.f_lineno)
    return trace

import faulthandler
faulthandler.enable()

#sys.settrace(trace)


class ToolsTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        
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
        
            
        self.layer = vl
        
        

    def tearDown(self):
        """Runs after each test."""

    def test_getUniqueValues(self):
        '''Test getUniqueValues'''
        values = getUniqueKeys(self.layer, 'name')
        self.assertEqual(len(values), 4)
    
    def test_getData(self):
        '''Test getData()'''
        data1 = [f for f in getData(self.layer, 'name', ['data1', 'data2'])]
        self.assertEqual(len(data1), 4)
        
        data2 = [f for f in getData(self.layer, 'name', ['data1', 'data2'])]
        self.assertEqual(len(data2), 4)
                
        data3 = [f for f in getData(self.layer, 'name', ['data1', 'data2', 'data1'])]
        self.assertEqual(len(data3), 4)

    def test_analyze(self):
        '''Test analiz'''
        dataIter = getData(self.layer, 'name', ['data1', 'data2'])
        def fun(data):
            res1 = 0
            res2 = 0
            for x, y in data:
               # print '(x, y) = ({}, {})'.format(x,y)
                if x  == '' or y == '':
                    pass
                else:
                    res1 += x
                    res2 += y
            return {'res1' : res1, 'res2' : res2}
            
        a = analyze(fun, dataIter)
        for thing in a:
            ite, datadict = thing
            features = [i for i in ite]
            self.assertTrue(len(features) > 10)
            self.assertEqual(type(datadict['res1']), float)
            self.assertEqual(type(datadict['res2']), float)

    def test_addFeatures(self):
        '''Test addFeatures'''
        dataIter = getData(self.layer, 'name', ['data1', 'data2'])
        def fun(data):
            res1 = 0
            res2 = 0
            for x, y in data:
               # print '(x, y) = ({}, {})'.format(x,y)
                if x  == '' or y == '':
                    pass
                else:
                    res1 += x
                    res2 += y
            return {'res1' : res1, 'res2' : res2}
            
        a = analyze(fun, dataIter)
        
        addFeatures(self.layer, a)
        
if __name__ == "__main__":
    suite = unittest.makeSuite(ToolsTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
