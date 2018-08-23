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

import unittest, sqlite3, os, csv

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
        self.interface.close()
        self.interface = None
        try:
            os.remove('./Analysis/test/testout.csv')
        except:
            pass
        try:
            os.remove('./Analysis/test/testout.sqlite')
        except:
            pass
    
    def test_loadMultipleFiles(self):
        '''Make sure a file cant be loaded twice'''
        val = self.interface.loadCSV('./Analysis/test/1.csv')
        self.assertFalse(val)
    
    def test_loadIncompatableFiles(self):
        '''Make sure that we dont load a file with bad columns'''
        tmp = DataInterface()
        names = ['DATE', 'STATION', 'TAVG', 'NAME', 'LATITUDE', 'LONGITUDE']
        tmp.setAttributeNames(names)
        tmp.initSQL()
        val = tmp.loadCSV('./Analysis/test/s2.csv')
        self.assertFalse(val)
        
    def test_UniqueKeys(self):
        '''See that we can get the unique columns in SQL database'''
        out = self.interface.pullUniqueKeys('STATION')
        self.assertEqual(len(out) , 62)
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

    def test_pullxydata(self):
        '''test that we can pull xy data for a station'''
        data = self.interface.pullXYData('STATION', 'USR0000WALD', 'DATE', 'TAVG')
        expected = [('1989', '43.6'), ('1995', '45.6'), ('2000', '45.1'), 
                    ('2001', '46.3'), ('2003', '47.3'), ('2005', '46.9'), 
                    ('2006', '46.7'), ('2007', '46.3'), ('2008', '45.2'), 
                    ('2009', '45.8'), ('2010', '45.7'), ('2011', '44.8'), 
                    ('2013', '46.8'), ('2016', '47.7'), ('2017', '46.9')]
                    
        intersect1 = set(data).symmetric_difference(expected)
        intersect2 = set(expected).symmetric_difference(data)
        self.assertEqual(len(intersect1), 0)
        self.assertEqual(len(intersect2), 0)
        
    def test_nosql(self):
        '''Make sure that error is thrown if we forget to init sql or 
        set attributes'''
        tmp = DataInterface()
        try:
            tmp.loadFolder('./Analysis/test/')
        except AttributeError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)
        
    def test_noattr(self):
        '''Make sure error is raised trying to init sql before
        attribute'''
        tmp = DataInterface()
        try:
            tmp.initSQL()
        except AttributeError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)
        
    def test_writecsv(self):
        '''make sure we can write out a csv'''
        self.interface.writeTableToCSV('./Analysis/test/testout.csv', self.interface.mainTableName)
        c = 0
        with open('./Analysis/test/testout.csv', 'r') as f:
            dr = csv.DictReader(f)
            for line in dr:
                c += 1
        self.assertEqual(c , 893)
        
    def test_emptydb(self):
        '''Make sure we handle at empty SQL db'''
        tmp = DataInterface()
        names = ['DATE', 'STATION', 'TAVG', 'NAME', 'LATITUDE', 'LONGITUDE']
        tmp.setAttributeNames(names)
        tmp.initSQL()
        try:
            tmp.connectMainSQL('./Analysis/test/empty.db', 'mainDBtable')
        except sqlite3.OperationalError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)
            
    def test_writesqlout(self):
        '''make sure that the databases are written out correctly'''
        self.interface.saveMainToDB('./Analysis/test/testout.sqlite', overwrite=False)
        tmp = DataInterface()
        names = ['DATE', 'STATION', 'TAVG', 'NAME', 'LATITUDE', 'LONGITUDE']
        tmp.setAttributeNames(names)
        tmp.initSQL()
        try:
            tmp.connectMainSQL('./Analysis/test/testout.sqlite')
        except sqlite3.OperationalError:
            self.assertTrue(False)
        else:
            self.assertTrue(True)
        

        
if __name__ == "__main__":
    suite = unittest.makeSuite(DataInterfaceTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
