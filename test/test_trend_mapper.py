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
from trend_mapper_tools import checkTrue
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
        
        self.layer = QgsVectorLayer(
                                    './test/test_noaa_yearly.sqlite', 
                                    'test_noaa_yearly', 'ogr')
        QgsMapLayerRegistry.instance().addMapLayer(self.layer)

        
        #set the category combo to the name field
        self.trendmapper.dlg.getCategoryCombo = lambda : 'station'
        
            
        
        

    def tearDown(self):
        """Runs after each test."""
        self.trendmapper.dlg = None
        self.trendmapper = None

    
    def test_dialoge(self):
        '''Test that the dialoge box loaded'''
        self.assertTrue(self.trendmapper.dlg is not None)

    def test_run_(self):
        '''Test that the run function works for int and float'''
        #set the xField combo
        self.trendmapper.dlg.getXFieldCombo = lambda : 'date'
        #set the yField combo
        self.trendmapper.dlg.getYFieldCombo = lambda : 'tavg'
        self.trendmapper.run(test_run = True)
    

  
if __name__ == "__main__":
    suite = unittest.makeSuite(TrendMapperTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
