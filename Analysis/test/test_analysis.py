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

from Analysis.data_interface import DataInterface
from Analysis.analysis import Analysis


class AnalysisTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.interface = DataInterface()
        self.interface.loadFolder('./Analysis/test/')
        self.interface.setCategoryLable('STATION')
        self.interface.setXLable('DATE')
        self.interface.setYLable('TAVG')
        self.interface.indexCSVFiles()

    def tearDown(self):
        """Runs after each test."""
        self.interface = None
        
    def test_loadFolder(self):
        '''Test load folder...'''
        pass

        


if __name__ == "__main__":
    suite = unittest.makeSuite(AnalysisTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
