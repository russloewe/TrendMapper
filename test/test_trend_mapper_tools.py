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
        
        

    def tearDown(self):
        """Runs after each test."""

    def test_getUniqueValues(self):
        '''Test getUniqueValues'''
        values = getUniqueKeys(self.layer, 'name')
        self.assertEqual(len(values), 4)
    
    def test_getData_intAndDouble(self):
        '''Test getData() for int and double columns'''
        data1 = [f for f in getData(self.layer, 'name', ['dataInt', 'dataDouble'])]
        self.assertEqual(len(data1), 4)
    
    def test_getData_intAndStr(self):
        '''Test getData() with int and str columns'''
        data2 = [f for f in getData(self.layer, 'name', ['dataInt', 'dataStr'])]
        self.assertEqual(len(data2), 4)
    
    def test_getData_threecol(self):
        '''Test getData() for more than two columns'''
        data3 = [f for f in getData(self.layer, 'name', ['dataInt', 'dataDouble', 'dataStr'])]
        self.assertEqual(len(data3), 4)

    def test_analyze(self):
        '''Test analyze'''
        dataIter = getData(self.layer, 'name', ['dataInt', 'dataDouble'])
        def fun(data):
            res1 = 0
            res2 = 0
            for x, y in data:
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
            for k in datadict:
                self.assertTrue(len(features) > 10)
                self.assertEqual(type(datadict['res1']), float)
                self.assertEqual(type(datadict['res2']), float)

    def test_addFeatures(self):
        '''Test addFeatures'''
        dataIter = getData(self.layer, 'name', ['dataInt', 'dataDouble'])
        def fun(data):
            res1 = 0
            res2 = 0
            for x, y in data:
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
