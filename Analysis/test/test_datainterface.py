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
        interface.close()
            
    
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
        interface.close()
        
    def test_initSQL_tableName(self):
        '''Make sure we can make a database with a different main table
        name'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'TAVG'])
        interface.initSQL(':memory:', mainTableName = 'differentName')
        self.assertNotEqual(interface.maincon, None)
        self.assertEqual(interface.mainTableName, 'differentName')
        interface.close()
        
    def test_initSQL_noconnect(self):
        '''Make sure we can initialize a database without connecting'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'TAVG'])
        interface.initSQL(':memory:', connect = False)
        self.assertEqual(interface.maincon, None)
        interface.close()
        
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
        interface.close()
    #############################################################
    #indexTable
    
    def test_indexTable_repeat(self):
        '''Make sure if we try to make an index that already exists
        that we get the right error'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION','TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.initSQL(':memory:')
        interface.loadFolder('./Analysis/test')
        interface.indexTable('newIndex', 'CSVData', 'STATION')
        interface.indexTable('newIndex', 'CSVData', 'STATION')
    #############################################################
    #pullUniqueKeys
    def test_pullUniqueKeys(self):
        '''Make sure that we get the right list of stations'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION','TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.initSQL(':memory:')
        interface.loadFolder('./Analysis/test')
        stations = interface.pullUniqueKeys('STATION')
        self.assertEqual(len(stations), 63)
        interface.close()
    
    def test_pullUniqueKeys_useIndex(self):
        '''Make sure that we get can use an index when getting 
        unique keys'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION','TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.initSQL(':memory:')
        interface.loadFolder('./Analysis/test')
        interface.indexTable('newindex', interface.mainTableName,
                                                            'STATION')
        stations = interface.pullUniqueKeys('STATION', 
                                                indexName = 'newindex')
        self.assertEqual(len(stations), 63)
        interface.close()
    #############################################################
    #dropTable
    
    def test_dropTable(self):
        '''Make sure the drop table function works'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION','TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.initSQL(':memory:')
        interface.loadFolder('./Analysis/test')
        interface.dropTable('CSVData')
        self.assertTrue('CSVData' not in interface.getTables())
        
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
        interface.close()
        
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
        interface.close()
        
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
        interface.close()
        
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
        try:
            interface.createGeoTable('', 'Station', 
                                           'LONGITUDE', 'LATITUDE')
        except sqlite3.OperationalError:
            pass
        else:
            self.fail('No error, or wrong error raised')
        interface.mainTableName = 'wrongtable'
        try:
            interface.createGeoTable('geomindex', 'NotStation', 
                                           'LONGITUDE', 'LATITUDE')
        except AttributeError:
            pass
        else:
            self.fail('AttributeError should have been raised')
        interface.close()
            
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
        interface.close()
            
    ##############################################################
    #connectMainSQL
    
    def test_connectMainSQL(self):
        '''Make sure we can connect to an sql table on the disk'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION', 'TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.connectMainSQL('./Analysis/test/geodata.db', 
                                           mainTableName = 'dataTable')
        self.assertTrue('dataTable' in interface.getTables())
        interface.close()
        
    def test_connectMainSQL_nofile(self):
        '''Make sure we dont create a new file if there is no file 
        on the disk'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION', 'TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        try:
            interface.connectMainSQL('./Analysis/test/nofile.db', 
                                           mainTableName = 'dataTable')
        except IOError:
            pass
        else:
            self.fail('An IOError exception should have been raised')
            
    def test_connectMainSQL_badtable(self):
        '''Make sure that we handle connecting to db with wrong 
        table name'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION', 'TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.initSQL(':memory:')
        try:
            interface.connectMainSQL('./Analysis/test/geodata.db', 
                                           mainTableName = 'wrongtable')
        except AttributeError:
            pass
        else:
            self.fail('There should have been a',
                                ' sqlite3.OperationalError raised')
        
    def test_connectMainSQL_nomaintable(self):
        '''Make sure we handle it when no main table is specified 
        as a param and there is not a self.mainTableName yet'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION', 'TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        try:
            interface.connectMainSQL('./Analysis/test/geodata.db')
        except AttributeError:
            pass
        else:
            self.fail('There should have been a',
                                ' sqlite3.OperationalError raised')
    
    def test_connectMainSQL_noMainTable(self):
        '''Make sure that using the fall back maintable name works'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION', 'TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.mainTableName = 'dataTable'
        interface.connectMainSQL('./Analysis/test/geodata.db')
        self.assertTrue('dataTable' in interface.getTables())
        
    def test_connectMainSQL_empytDB(self):
        '''Make sure that using connecting to an empty 
        database gives the right error'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION', 'TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        try:
            interface.connectMainSQL('./Analysis/test/empty.db',
                                mainTableName = 'dataTable')
        except AttributeError:
            pass
        else:
            self.fail('Last call should have raised an attributeerror')
       
    def test_connectMainSQL_wrongAttributeCol(self):
        '''Make sure that using connecting to an empty 
        database gives the right error'''
        interface = DataInterface()
        interface.setAttributeNames(['wrongattr', 'STATION', 'TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        try:
            interface.connectMainSQL('./Analysis/test/geodata.db',
                                        mainTableName = 'dataTable')
        except AttributeError:
            pass
        else:
            self.fail('Last call should have raised an attributeerror')
            
    ###############################################################
    #loadCSV
    
    def test_loadCSV_repeatedFiles(self):
        '''Make sure we handle trying to load the same file 
        twice correctly'''
        interface = DataInterface()
        interface.setAttributeNames([ 'STATION', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.initSQL(':memory:')
        self.assertTrue(interface.loadCSV('./Analysis/test/1.csv'))
        self.assertFalse(interface.loadCSV('./Analysis/test/1.csv'))
        
    def test_loadCSV_badFile(self):
        '''Make sure we handle trying to load the same file 
        twice correctly'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'notattr', 'TAVG'])
        interface.initSQL(':memory:')
        self.assertFalse(interface.loadCSV('./Analysis/test/s1.csv'))
        
    def test_loadFolder(self):
        '''Make sure we can load a folder and that all the 
        attributes got loaded'''
        interface = DataInterface()
        names = ['DATE', 'STATION','TAVG', 'LONGITUDE', 'LATITUDE']
        interface.setAttributeNames(names)
        interface.initSQL(':memory:')
        interface.loadFolder('./Analysis/test')
        for name in names:
            self.assertTrue(len(interface.pullUniqueKeys(name)) > 10)
        
    
    ################################################################
    #writeTableToCSV
    
    def test_writeTableToCSV(self):
        '''Make sure we can export a table to a CSV file'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION','TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.initSQL(':memory:')
        interface.loadFolder('./Analysis/test')
        interface.writeTableToCSV('./Analysis/test/testout.csv', 
                                    interface.mainTableName)
        c = 0
        with open('./Analysis/test/testout.csv', 'r') as f:
            dr = csv.DictReader(f)
            for line in dr:
                c += 1
        self.assertEqual(c , 874)

    ################################################################
    #pullXYData
    
    def test_pullXYData(self):
        '''Make sure we can pull data'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION','TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.initSQL(':memory:')
        interface.loadFolder('./Analysis/test')
        data = interface.pullXYData('STATION', 'USR0000WALD', 'DATE', 
                                                              'TAVG')
        expected = [(1989, 43.6), (1995, 45.6), (2000, 45.1), 
                    (2001, 46.3), (2003, 47.3), (2005, 46.9), 
                    (2006, 46.7), (2007, 46.3), (2008, 45.2), 
                    (2009, 45.8), (2010, 45.7), (2011, 44.8), 
                    (2013, 46.8), (2016, 47.7), (2017, 46.9)]
                    
        intersect1 = set(data).symmetric_difference(expected)
        intersect2 = set(expected).symmetric_difference(data)
        self.assertEqual(len(intersect1), 0)
        self.assertEqual(len(intersect2), 0)
        
    def test_pullXYData_useIndex(self):
        '''Make sure we can create an index and use it to pull data'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION','TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.initSQL(':memory:')
        interface.loadFolder('./Analysis/test')
        interface.indexTable('newIndex', interface.mainTableName,
                                                    'STATION')
        data = interface.pullXYData('STATION', 'USR0000WALD', 'DATE', 
                                    'TAVG', indexName = 'newIndex')
        self.assertEqual(len(data), 15)
        #this next station has a blank 'TAVG' entry, make sure 
        data = interface.pullXYData('STATION', 'USR0000CKLA', 'DATE', 
                                    'TAVG', indexName = 'newIndex') 
        self.assertEqual(len(data), 12)
       
       
    def test_pullUniqueKeys_wrongIndex(self):
        '''Make sure we get the right error if we try to use a 
        non existant index or the wrong index'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION','TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.initSQL(':memory:')
        interface.loadFolder('./Analysis/test')
        try:
            interface.pullXYData('STATION', 'USR0000CKLA', 
                        'DATE', 'TAVG', indexName = 'noIndex')
        except sqlite3.OperationalError:
            pass
        else:
            self.fail('There should have been an "no index" execption'\
                                                            'raised')
        interface.indexTable('newIndex', interface.mainTableName,
                                                    'LATITUDE')
        try:
            interface.pullXYData('STATION', 'USR0000CKLA', 
                        'DATE', 'TAVG', indexName = 'newIndex')
        except sqlite3.OperationalError:
            pass
        else:
            self.fail('There should have been an sqlite operational'\
                                                            'error')
    #################################################################
    #writeMainConToDB
    
    def test_writeMainConToDB_disk(self):
        '''Make sure we can write the main database connection to
        a database on the disk'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION','TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.initSQL(':memory:')
        interface.loadFolder('./Analysis/test')
        interface.saveMainConToDB('./Analysis/test/testout.sqlite')
        
        if not os.path.isfile('./Analysis/test/testout.sqlite'):
            self.fail('No file on disk after trying to save database')
        interface.connectMainSQL('./Analysis/test/testout.sqlite')
        self.assertTrue(interface.mainTableName in interface.getTables())
        
    def test_writeMainConToDB_diskoverwrite(self):
        '''Make sure we can write the main database connection to
        a database on the disk and overwrite it'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION','TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.initSQL(':memory:')
        interface.loadFolder('./Analysis/test')
        #save a database
        interface.saveMainConToDB('./Analysis/test/testout.sqlite')
        self.assertTrue('differentTable' not in interface.getTables())
        interface.initSQL(':memory:', mainTableName = 'differentTable')
        interface.saveMainConToDB('./Analysis/test/testout.sqlite',
                                            overwrite = True)
        interface.connectMainSQL('./Analysis/test/testout.sqlite')
        self.assertTrue('differentTable' in interface.getTables())
        
    def test_writeMainConToDB_memattach(self):
        '''Make sure we can write a database from the disk to mem
        and connect to it'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION','TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.connectMainSQL('./Analysis/test/geodata.db', 
                                    mainTableName = 'dataTable')
        #save a ref to the current db con
        con = interface.maincon
        interface.saveMainConToDB(':memory:', attach = True)
        con2 = interface.maincon
        self.assertNotEqual(con, con2)
        self.assertTrue('dataTable' in interface.getTables())
        
   
   ##################################################################
    #filter
    def test_filter(self):
        '''make sure the filter by location works'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION','TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.initSQL(':memory:')
        interface.loadFolder('./Analysis/test')
        interface.createGeoTable('geomindex', 'STATION',
                                                'LONGITUDE', 'LATITUDE')
        result = interface.filter('STATION', 
        './Analysis/test/states.sqlite', 'geomindex', 'states',
                                        'GEOMETRY' , 'GEOMETRY')
        self.assertEqual(len(result), 60)
        self.assertFalse('TEST' in result)
        
    def test_filter_badmasktable(self):
        '''make sure the filter by location catches bad
        params'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION','TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.initSQL(':memory:')
        interface.loadFolder('./Analysis/test')
        interface.createGeoTable('geomindex', 'STATION',
                                                'LONGITUDE', 'LATITUDE')
        try:
            interface.filter('STATION', './Analysis/test/states.sqlite',
                      'geomindex', 'badTable', 'GEOMETRY' , 'GEOMETRY')
        except sqlite3.OperationalError:
            pass
        else:
            self.fail('Sqlite op error should have been raised')
    
    def test_filter_badfile(self):
        '''make sure the filter by location catches bad filename'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION','TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.initSQL(':memory:')
        interface.loadFolder('./Analysis/test')
        interface.createGeoTable('geomindex', 'STATION',
                                                'LONGITUDE', 'LATITUDE')
        try:
            interface.filter('STATION', './Analysis/test/nofile.sqlite',
                        'geomindex', 'states', 'GEOMETRY' , 'GEOMETRY')
        except sqlite3.OperationalError:
            pass
        else:
            self.fail('Sqlite op error should have been raised')
            
    ################################################################
    #applyFunction
    
    def test_applyFunction(self):
        '''Make sure that we can apply a fuction to the dataset'''
        interface = DataInterface()
        interface.setAttributeNames(['DATE', 'STATION','TAVG', 
                                     'LONGITUDE', 'LATITUDE'])
        interface.initSQL(':memory:')
        interface.loadFolder('./Analysis/test')
        interface.createGeoTable('geoTable', 'STATION',
                                                'LONGITUDE', 'LATITUDE')
        stations = interface.pullUniqueKeys('STATION',
                                                tableName = 'geoTable')
        interface.applyFunction('STATION', stations, 'DATE', 'TAVG', 
                                    'geoTable', lambda x : {'result':1}) 
        if 'result' not in interface.getTableAttributes('geoTable'):
            self.fail('result column not present in dest Table')
        rs = interface.pullUniqueKeys('result', tableName = 'geoTable')
        self.assertTrue( '1.0' in rs)
    
        
if __name__ == "__main__":
    suite = unittest.makeSuite(DataInterfaceTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
