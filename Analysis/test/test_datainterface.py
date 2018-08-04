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


class DataInterfaceTest(unittest.TestCase):
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
        fileList = self.interface.getCSVFileList(filterInvalid=False)
        self.assertEqual(len(fileList) , 6)
        fileList = self.interface.getCSVFileList(filterInvalid=True)
        self.assertEqual(len(fileList) , 5)
        
    def test_lableSetters(self):
        '''See if we can set the x, y lables'''
        self.assertEqual(self.interface.categoryLable, 'STATION')
        self.assertEqual(self.interface.xLable, 'DATE')
        self.assertEqual(self.interface.yLable, 'TAVG')
        
    def test_indexFiles(self):
        '''See if the file indexer works'''
        for f in self.interface.csvFiles:
            if f.validLables:
                self.assertTrue(len(f.indexDict) > 0)
        
    def test_FileCounts(self):
        '''See if the file counts work'''
        
        allFiles = self.interface.getFileCountAll()
        validFiles = self.interface.getFileCountValid()
        
        self.assertEqual(allFiles, 6)
        self.assertEqual(validFiles, 5)

if __name__ == "__main__":
    suite = unittest.makeSuite(DataInterfaceTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
