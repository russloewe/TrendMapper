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

from PyQt4.QtGui import QDialogButtonBox, QDialog, QWidget
from trend_mapper import TrendMapper

from qgis.gui import QgsMapCanvas
from qgis_interface import QgisInterface
from utilities import get_qgis_app
from PyQt4.QtCore import QSettings


QGIS_APP = get_qgis_app()


class TrendMapperTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.iface = QgisInterface(QgsMapCanvas(QWidget()))
        self.trendMapper = TrendMapper(self.iface)

    def tearDown(self):
        """Runs after each test."""
        self.trendMapper = None
        
    def test_attributeCallback(self):
        '''see if calling the call back function gives errors'''
      #  self.trendMapper.updateAttributeCombos()
        pass

if __name__ == "__main__":
    suite = unittest.makeSuite(TrendMapperTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
