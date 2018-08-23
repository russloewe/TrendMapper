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

import unittest, sqlite3

from Analysis.data_interface import DataInterface


class DataInterfaceTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.interface = DataInterface()
        names = ['DATE', 'STATION', 'TAVG', 'NAME', 'LATITUDE', 'LONGITUDE']
        self.interface.setAttributeNames(names)
        self.interface.initSQL()
        self.interface.loadFolder('./Analysis/test/')

    def tearDown(self):
        """Runs after each test."""
        self.interface = None
        
    def testUniqueKeys(self):
        '''See that we can get the unique columns in SQL database'''
        out = self.interface.pullUniqueKeys('STATION')
        self.assertTrue(len(out) > 20)
        try:
            self.interface.pullUniqueKeys('TTT')
        except sqlite3.OperationalError:
            self.assertTrue(True) 
        else:
            self.assertTrue(False) #was supposed to throw exception
        
    def test_attributeNamesLoaded(self):
        '''Make sure that the attribute names were inserted into 
        SQL '''
        for name in ['DATE', 'STATION', 'TAVG', 'NAME', 'LATITUDE', 'LONGITUDE']:
            self.interface.pullUniqueKeys(name)


        
if __name__ == "__main__":
    suite = unittest.makeSuite(DataInterfaceTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
