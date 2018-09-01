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
from Analysis.example import runner1
from Analysis.data_interface import DataInterface


class DataInterfaceTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""

    def tearDown(self):
        """Runs after each test."""
        try:
            os.remove('./Analysis/test/testout.csv')
        except:
            pass
        try:
            os.remove('./Analysis/test/testout.sqlite')
        except:
            pass
        try:
            os.remove('./test.db')
        except:
            pass
    ###########################################################
    # initSQL()
    
    def test_initSQL_noAttributes(self):
        '''Make sure we dont proceed with out attributes specified'''
        interface = DataInterface()
        try:
            interface.initSQL('')
        except AttributeError:
            pass
        else:
            self.fail('An error should have been raised')   
            
    
    def test_initSQL_overwriteFile(self):
        '''Make sure we can overwrite a database on the disk'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'TAVG'])
        open('./test.db', 'w').close() #make temp file
        try:
            interface.initSQL('./test.db')
        except IOError:
            pass
        else:
            self.fail('An error should have been raised')  
        interface.initSQL('./test.db', overwrite = True, 
                                        spatialite = False)
        self.assertEqual(type(interface.maincon), sqlite3.Connection)
        
    def test_initSQL_tableName(self):
        '''Make sure we can make a database with a different main table
        name'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'TAVG'])
        interface.initSQL(':memory:', mainTableName = 'differentName')
        self.assertNotEqual(interface.maincon, None)
        self.assertEqual(interface.mainTableName, 'differentName')
        
    def test_initSQL_noconnect(self):
        '''Make sure we can initialize a database without connecting'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'TAVG'])
        interface.initSQL(':memory:', connect = False)
        self.assertEqual(interface.maincon, None)
        
    #############################################################
    #checkmaincon
    
    def test_getMainCur(self):
        '''Make sure the checkMainCon function works as expected'''
        interface = DataInterface()
        try:
            interface.getMainCur()
        except AttributeError:
            pass
        else:
            self.fail('There should have been an attirbute exception')
        interface.maincon = 1
        try:
            interface.getMainCur()
        except AttributeError:
            pass
        else:
            self.fail('There should have been an attirbute exception')
        interface.setAttributeNames(['DATE', 'TAVG'])
        interface.initSQL(':memory:')
        cur = interface.getMainCur()
        self.assertEqual(type(cur), sqlite3.Cursor)
    
    #############################################################
    #pullUniqueKeys
    def test_pullUniqueKeys(self):
        '''Make sure that we get the right list of stations'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION','TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.initSQL(':memory:')
        interface.loadFolder('./Analysis/test')
        interface.pullUniqueKeys('STATION')
    
    #############################################################
    #createGeoTable
    def test_createGeoTable(self):
        '''Test that we can make a geo table'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION', 'TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.initSQL(':memory:')
        interface.createGeoTable('geomindex', 'STATION', 'LONGITUDE',
                                                          'LATITUDE')
        self.assertTrue('geomindex' in interface.getTables())
        
    def test_createGeoTable_keysubset(self):
        '''Test that the key subset param works'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION', 'TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.initSQL(':memory:')
        interface.loadFolder('./Analysis/test')
        interface.createGeoTable('geomindex', 'STATION', 'LONGITUDE',
                'LATITUDE', keySubset = ['USR0000OECK', 'USR0000ONPR'])
        stations = interface.pullUniqueKeys('STATION', 
                                               tableName = 'geomindex')
        self.assertEqual(len(stations), 2)
        self.assertTrue('USR0000OECK' in stations)
        self.assertTrue('USR0000ONPR' in stations)
        
    def test_creatGeoTable_spatialite(self):
        '''Make a geotable on a database without spatialite metadata yet'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION', 'TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.initSQL(':memory:', spatialite = False)
        interface.loadFolder('./Analysis/test')
        interface.createGeoTable('geomindex', 'STATION', 'LONGITUDE',
                                    'LATITUDE', initSpatialite = True)
        stations = interface.pullUniqueKeys('STATION', 
                                               tableName = 'geomindex')
        self.assertEqual(len(stations), 63)
        
    def test_creatGeoTable_badTable(self):
        '''Make sure that right exceptions are raised for bad params'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION', 'TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.initSQL(':memory:')
        interface.loadFolder('./Analysis/test')
        try:
            interface.createGeoTable('geomindex', 'NotStation', 
                                           'LONGITUDE', 'LATITUDE')
        except sqlite3.OperationalError:
            pass
        else:
            self.fail('No error, or wrong error raised')
            
    def test_creatGeoTable_noTable(self):
        '''Make sure that we catch no table'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION', 'TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        try:
            interface.createGeoTable('geomindex', 'STATION', 
                                           'LONGITUDE', 'LATITUDE')
        except AttributeError:
            pass
        else:
            self.fail('The last fuction should have thrown an' \
                       ' an attribute execption')
        interface.initSQL(':memory:')
        interface.mainTableName = None
        try:
            interface.createGeoTable('geomindex', 'STATION', 
                                           'LONGITUDE', 'LATITUDE')
        except AttributeError:
            pass
        else:
            self.fail('Last call should have raised an attribute exception')
            
    ##############################################################
    def _test_loadMultipleFiles(self):
        '''Make sure a file cant be loaded twice'''
        val = self.interface.loadCSV('./Analysis/test/1.csv')
        self.assertFalse(val)
    
    def _test_loadIncompatableFiles(self):
        '''Make sure that we dont load a file with bad columns'''
        tmp = DataInterface()
        names = ['DATE', 'STATION', 'TAVG', 'NAME', 'LATITUDE', 'LONGITUDE']
        tmp.setAttributeNames(names)
        tmp.initSQL('')
        val = tmp.loadCSV('./Analysis/test/s2.csv')
        self.assertFalse(val)
        
    def _test_UniqueKeys(self):
        '''See that we can get the unique columns in SQL database'''
        out = self.interface.pullUniqueKeys('STATION')
        self.assertEqual(len(out) , 63)
        self.interface.pullUniqueKeys('STATION', 'CSVData')
        try:
            self.interface.pullUniqueKeys('TTT')
        except sqlite3.OperationalError:
            self.assertTrue(True) 
        else:
            self.assertTrue(False) #was supposed to throw exception
        
    def _test_attributeNamesLoaded(self):
        '''Make sure that the attribute names were inserted into 
        SQL '''
        for name in ['DATE', 'STATION', 'TAVG', 'NAME', 'LATITUDE', 'LONGITUDE']:
            self.interface.pullUniqueKeys(name)

    def _test_pullxydata(self):
        '''test that we can pull xy data for a station'''
        data = self.interface.pullXYData('STATION', 'USR0000WALD', 'DATE', 'TAVG')
        expected = [(1989, 43.6), (1995, 45.6), (2000, 45.1), 
                    (2001, 46.3), (2003, 47.3), (2005, 46.9), 
                    (2006, 46.7), (2007, 46.3), (2008, 45.2), 
                    (2009, 45.8), (2010, 45.7), (2011, 44.8), 
                    (2013, 46.8), (2016, 47.7), (2017, 46.9)]
                    
        intersect1 = set(data).symmetric_difference(expected)
        intersect2 = set(expected).symmetric_difference(data)
        self.assertEqual(len(intersect1), 0)
        self.assertEqual(len(intersect2), 0)
        
    def _test_nosql(self):
        '''Make sure that error is thrown if we forget to init sql or 
        set attributes'''
        tmp = DataInterface()
        try:
            tmp.loadFolder('./Analysis/test/')
        except AttributeError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)
        
    def _test_noattr(self):
        '''Make sure error is raised trying to init sql before
        attribute'''
        tmp = DataInterface()
        try:
            tmp.initSQL('')
        except AttributeError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)
        
    def _test_writecsv(self):
        '''make sure we can write out a csv'''
        self.interface.writeTableToCSV('./Analysis/test/testout.csv', self.interface.mainTableName)
        c = 0
        with open('./Analysis/test/testout.csv', 'r') as f:
            dr = csv.DictReader(f)
            for line in dr:
                c += 1
        self.assertEqual(c , 874)
        
    def _test_emptydb(self):
        '''Make sure we handle at empty SQL db'''
        tmp = DataInterface()
        names = ['DATE', 'STATION', 'TAVG', 'NAME', 'LATITUDE', 'LONGITUDE']
        tmp.setAttributeNames(names)
        tmp.initSQL('')
        try:
            tmp.connectMainSQL('./Analysis/test/empty.db', 'mainDBtable')
        except sqlite3.OperationalError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)
            
    def _test_writesqlout(self):
        '''make sure that the databases are written out correctly'''
        self.interface.saveMainConToDB('./Analysis/test/testout.sqlite', overwrite=False)
        tmp = DataInterface()
        names = ['DATE', 'STATION', 'TAVG', 'NAME', 'LATITUDE', 'LONGITUDE']
        tmp.setAttributeNames(names)
        tmp.initSQL('')
        try:
            tmp.connectMainSQL('./Analysis/test/testout.sqlite')
        except sqlite3.OperationalError:
            self.assertTrue(False)
        else:
            self.assertTrue(True)
            
        
        
    def _test_geomindex(self):
        '''make sure we can create a geo table for our data'''
        self.interface.createGeoTable('geomindex', 'STATION', 'LONGITUDE', 'LATITUDE')
        
        list1 = self.interface.pullUniqueKeys('STATION')
        list2 = self.interface.pullUniqueKeys( 'STATION', tableName='geomindex')
        intersect1 = set(list1).symmetric_difference(list2)
        intersect2 = set(list2).symmetric_difference(list1)
        self.assertEqual(len(intersect1), 0)
        self.assertEqual(len(intersect2), 0)
        #make sure geometry is not none
        list3 = self.interface.pullUniqueKeys( 'GEOMETRY', tableName='geomindex')
        self.assertFalse('None' in list3)
        self.interface.createGeoTable('geomindex', 'STATION', 'LONGITUDE', 'LATITUDE') #make sure it doesnt trip up running twice
        
        #make sure that it can index a plain sql db
        interface = DataInterface()
        names = ['DATE', 'STATION', 'TAVG', 'NAME', 'LATITUDE', 'LONGITUDE']
        interface.setAttributeNames(names)
        interface.initSQL('', spatialite=False)
        interface.loadFolder('./Analysis/test/')
        interface.createGeoTable('geomindex', 'STATION', 'LONGITUDE', 'LATITUDE', initSpatialite=True)

        
    def _test_index(self):
        '''Make sure that the sql column indexer works'''
        self.interface.indexTable('stationIndex', self.interface.mainTableName, 'STATION')
        self.interface.indexTable('stationIndex', self.interface.mainTableName, 'STATION')
        stations = self.interface.pullUniqueKeys('STATION')

    def _test_filter(self):
        '''make sure the filter location works'''
        self.interface.createGeoTable('geomindex', 'STATION', 'LONGITUDE', 'LATITUDE')
        result = self.interface.filter('STATION', './Analysis/test/states.sqlite', 'geomindex', 'states', 'GEOMETRY' , 'GEOMETRY')
        self.assertEqual(len(result), 60)
        self.assertFalse('TEST' in result)
        
        
if __name__ == "__main__":
    suite = unittest.makeSuite(DataInterfaceTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
