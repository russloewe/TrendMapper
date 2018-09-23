# coding=utf-8
"""Tools test.

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
def convFun(point):
    for key in point:
        if type(point[key]) != QgsGeometry:
            point[key] = str(point[key])
    return point

class ToolsTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.layer_yearly = QgsVectorLayer(
                                    './test/test_noaa_yearly.sqlite', 
                                    'test_noaa_yearly', 'ogr')
        self.layer_monthly = QgsVectorLayer(
                                    './test/test_noaa_monthly.sqlite',
                                     'test_noaa_monthly', 'ogr')
        self.layer_daily = QgsVectorLayer(
                                    './test/test_noaa_daily.sqlite', 
                                    'test_noaa_daily', 'ogr')
        QgsMapLayerRegistry.instance().addMapLayer(self.layer_yearly)
        

    def tearDown(self):
        """Runs after each test."""
        self.layer_yearl = None
        self.layer_monthly = None
        self.layer_dialy = None

    def test_getUniqueValues(self):
        '''Test getUniqueValues'''
        values_yearly = getUniqueKeys(self.layer_yearly, 'STATION')
        values_monthly = getUniqueKeys(self.layer_monthly, 'STATION')
        values_daily = getUniqueKeys(self.layer_daily, 'STATION')
        self.assertEqual(len(values_yearly), 5)
        self.assertEqual(len(values_monthly), 1)
        self.assertEqual(len(values_daily), 5)
    
    def test_getUniqueValues_wrongname(self):
        '''Test getUniqueValues with wrong column name'''
        try:
            values_yearly = getUniqueKeys(self.layer_yearly, 'wrongname')
        except ValueError:
            pass
        else:
            self.fail("A ValueError exception should have been raised "\
                      "for non-existant column name.")
    
    def test_featureGenerator(self):
        '''test the feature generator'''
        stationNames = ['USC00393316', 'USW00094040', 'USS0011J06S',
                                       'USC00126420', 'USW00024152']
        for station in stationNames:
            features = [f for f in featureGenerator(self.layer_yearly, 
                                            station, 'STATION')]
            for f in features:
                self.assertEqual(len(features), 8)
                
    def test_datapointGenerator(self):
        '''Test the datapointGenerator'''
        stationNames = ['USC00393316', 'USW00094040', 'USS0011J06S',
                                       'USC00126420', 'USW00024152']
        for station in stationNames:
            featureIter = self.layer_yearly.getFeatures(
                            QgsFeatureRequest().setFilterExpression(
                                                 "{} = '{}'".format(
                                            'STATION', station)))
            datagen = datapointGenerator(featureIter, ['DATE', 'TAVG', 
                                                   'STATION'])
            data = [point for point in datagen]
            self.assertEqual(len(data), 8)
            for point in data:
                self.assertTrue('DATE' in point)
                self.assertTrue('TAVG' in point)
                self.assertTrue('STATION' in point)
                self.assertEqual(type(point['GEOMETRY']), QgsGeometry)
                
    def test_filterDatapointGenerator(self):
        '''Test the filterDatapointGenerator function'''
        stationNames = ['USC00393316', 'USW00094040', 'USS0011J06S',
                                       'USC00126420', 'USW00024152']
        for station in stationNames:
            featureIter = self.layer_yearly.getFeatures(
                            QgsFeatureRequest().setFilterExpression(
                                                 "{} = '{}'".format(
                                            'STATION', station)))
            datagen = datapointGenerator(featureIter, ['DATE', 'TAVG', 
                                                   'STATION'])
            filtered = filterDatapointGenerator(datagen, filterFun)
            data = [f for f in filtered]
            if station == 'USS0011J06S':
                self.assertTrue(len(data) == 0)
            else:
                self.assertTrue(len(data) >= 3)
            for point in data:
                for key in point:
                    self.assertTrue(point[key] != NULL)
            
    def test_convertDatapointGenerator_tostr(self):
        '''test the convertDatapointGenerator function'''
        
            
        stationNames = ['USC00393316', 'USW00094040', 'USS0011J06S',
                                       'USC00126420', 'USW00024152']
        for station in stationNames:
            featureIter = self.layer_yearly.getFeatures(
                            QgsFeatureRequest().setFilterExpression(
                                                 "{} = '{}'".format(
                                            'STATION', station)))
            datagen = datapointGenerator(featureIter, ['DATE', 'TAVG', 
                                                   'STATION'])
            filtered = filterDatapointGenerator(datagen, filterFun)
            conv = convertedDatapointGenerator(filtered, convFun)
            
            data = [ p for p in conv]
            if station == 'USS0011J06S':
                self.assertTrue(len(data) == 0)
            else:
                self.assertTrue(len(data) >= 3)
            for point in data:
                for key in point:
                    if key not in 'GEOMETRY':
                        self.assertEqual(type(point[key]), str)
    
    def test_convertDatapointGenerator_tofloat(self):
        '''test the convertDatapointGenerator function'''
        
            
        stationNames = ['USC00393316', 'USW00094040', 'USS0011J06S',
                                       'USC00126420', 'USW00024152']
        for station in stationNames:
            featureIter = self.layer_yearly.getFeatures(
                            QgsFeatureRequest().setFilterExpression(
                                                 "{} = '{}'".format(
                                            'STATION', station)))
            datagen = datapointGenerator(featureIter, ['DATE', 'TAVG', 
                                                   'STATION'])
            filtered = filterDatapointGenerator(datagen, filterFun)
            conv = convertedDatapointGenerator(filtered, convFunNum(['DATE', 'TAVG']), skipOnErr = True)
            
            data = [ p for p in conv]
            if station == 'USS0011J06S':
                self.assertTrue(len(data) == 0)
            else:
                self.assertTrue(len(data) >= 3)
            for point in data:
                for key in point:
                    if key in ['DATE', 'TAVG']:
                        self.assertEqual(type(point[key]), float)
    def test_convertDatapointGenerator_exception(self):
        '''Test the convertDatapointGenerator when the conv function 
        raises exception'''
        station = 'USC00393316'
        points = [{'date' : 1, 'year' : 'a'}, 
                  {'date' : 1, 'year' : 'a'}]
        def errorFun(a):
            raise Exception('exception')
        conv1 = convertedDatapointGenerator(points, errorFun , 
                                                    skipOnErr = True)
        conv2 = convertedDatapointGenerator(points, errorFun , 
                                                    skipOnErr = False)
        for i in conv1:
            pass
        try:
            conv2.next()
        except Exception:
            pass
        else:
            self.fail('Last call should have raised exception')
            
    def test_organizeData(self):
        '''Test the organizeData function'''
        stationNames = ['USC00393316', 'USW00094040', 'USS0011J06S',
                                       'USC00126420', 'USW00024152']
        for station in stationNames:
            featureIter = self.layer_yearly.getFeatures(
                            QgsFeatureRequest().setFilterExpression(
                                                 "{} = '{}'".format(
                                            'STATION', station)))
            datagen = datapointGenerator(featureIter, ['DATE', 'TAVG', 
                                                   'STATION'])
            filtered = filterDatapointGenerator(datagen, filterFun)
            conv = convertedDatapointGenerator(filtered, convFunNum(['DATE', 'TAVG']), skipOnErr = True)
            
            data = organizeData(conv, ['DATE', 'TAVG'])
    
    def test_createVectorLayer(self):
        '''Test createVectorLayer function'''
        attr = ['station', 'date', 'longitude']
        newLayer = createVectorLayer(self.layer_yearly, 'new', attr)
        newFields = []
        for i in newLayer.pendingFields():
            newFields.append(str(i.name()))
        for name in attr:
            if name not in newFields:
                self.fail('{} not in new layer fields'.format(name))
    
    def test_createVectorLayer_noname(self):
        '''Test the createVectorLayer with no name provided'''
        attr = ['station', 'date', 'longitude']
        try:
            newLayer = createVectorLayer(self.layer_yearly, '', attr)
        except ValueError:
            pass
        else:
            self.fail('There should have been a ValueError')
            
    def test_createVectorLayer_wrongCol(self):
        '''Test createVectorLayer with wrong column name'''
        attr = ['---station', '---date', '---longitude']
        try:
            newLayer = createVectorLayer(self.layer_yearly, 'new', attr)
        except AttributeError:
            pass
        else:
            self.fail('AttributeError should have been raised for wrong'\
                      ' column name')
    def test_getLayerByName(self):
        '''Test the getLayerByName function'''
        layer = getLayerByName('test_noaa_yearly')
        self.assertEqual(str(layer.name()), 'test_noaa_yearly')
        try:
            layer = getLayerByName('noLayer')
        except AttributeError:
            pass
        else:
            self.fail('The last call should have raised an'\
                                                ' AttributeError')
    def test_checker(self):
        ''' Test the checker function'''
        def false():
            return False
        def true():
            return True
        checkTrue(true())
        try:
            checkTrue(false())
        except ValueError:
            pass
        else:
            self.fail('last call should have raised exception')
    
    def test_convertFun(self):
        '''test the convert function with the date converter'''
        test = {'x' : '2.0', 'y' : 'test', 'd' : '2018-12-28'}
        function = convFunNum(['x'])
        converted = function(test)
        self.assertEqual(type(converted['x']), float)
        function = convFunNum(['x'], dateColumn = 'd', dateFormat = '%Y-%m-%d')
        converted = function(test)
        self.assertEqual(converted['d'], 737056)
    
    def test_makeFeature(self):
        '''Test the makeFeature function'''
        featureDict = {'date' : 2014, 'station' : 'new', 'GEOMETRY' : QgsGeometry()}
        feature = makeFeature(self.layer_yearly, featureDict)
        self.assertEqual(type(feature), QgsFeature)
        
    def test_makeFeature_nogeom(self):
        '''Test the makeFeature function with no geometry'''
        featureDict = {}
        try:
            makeFeature(self.layer_yearly, featureDict)
        except KeyError:
            pass
        else:
            self.fail('the last call should have raised KeyError')
        
    def test_addResultFields(self):
        '''Test the addResultFields function'''
        attr = ['station', 'date', 'longitude']
        newLayer = createVectorLayer(self.layer_yearly, 'new', attr)
        result = {'slope' : 3, 'mean' : 4}
        addResultFields(newLayer, result)
        self.assertTrue('slope' in [str(i.name()) for i in newLayer.pendingFields()])
        
if __name__ == "__main__":
    suite = unittest.makeSuite(ToolsTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
