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
        self.layer_yearly = QgsVectorLayer('./test/test_noaa_yearly.sqlite', 'test_noaa_yearly', 'ogr')
        self.layer_monthly = QgsVectorLayer('./test/test_noaa_monthly.sqlite', 'test_noaa_monthly', 'ogr')
        self.layer_daily = QgsVectorLayer('./test/test_noaa_daily.sqlite', 'test_noaa_daily', 'ogr')
        
        

    def tearDown(self):
        """Runs after each test."""

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
            features = [f for f in featureGenerator(self.layer_yearly, station, 
                                                            'STATION')]
            for f in features:
            self.assertEqual(len(features), 8)
                
        
        
if __name__ == "__main__":
    suite = unittest.makeSuite(ToolsTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
