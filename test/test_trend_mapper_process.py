# coding=utf-8
"""TrendMapperProcess test.

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
from trend_mapper_process import TrendMapperProcess

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

class ProcessTest(unittest.TestCase):
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

    def test_getUniqueValues(self):
        '''Test getUniqueValues'''
        pass
    
        
if __name__ == "__main__":
    suite = unittest.makeSuite(ProcessTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
