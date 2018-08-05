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
        
        #init the data interface to generate test data for the
        #analysis module
        self.interface = DataInterface()
        self.interface.loadFolder('./Analysis/test/')
        self.interface.setCategoryLable('STATION')
        self.interface.setXLable('DATE')
        self.interface.setYLable('TAVG')
        self.interface.addCopyAttributeLable('LATITUDE')
        self.interface.addCopyAttributeLable('LONGITUDE')
        self.interface.indexCSVFiles()
        self.interface.indexCategories()
        self.testData = []
        stations = self.interface.getCategoryList()
        for station in stations:
            data = self.interface.getCategoryDataset(station)
            self.testData.append(data)
        
        self.analysis = Analysis()
    
    def test_linearRegression(self):
        '''Test that linear regression passes some test calculation'''
        testData1 = [(x, x) for x in range(10)]
        testData2 = [(x, x*2) for x in range(10)]
        testData3 = [(x, x*3+4) for x in range(10)]
        testData4 = [(x, x) for x in range(1)]
        result1 = self.analysis.calculateLinearRegression(testData1)
        result2 = self.analysis.calculateLinearRegression(testData2)
        result3 = self.analysis.calculateLinearRegression(testData3)
        result4 = self.analysis.calculateLinearRegression(testData4)
        self.assertTrue(abs(result1['slope'] - 1.0) < .0000001)
        self.assertTrue(abs(result1['intercept'] -0) < .0000001)
        self.assertEqual(result1['rank'], 2)
        
        self.assertTrue(abs(result2['slope'] -2) < .0001)
        self.assertTrue(abs(result2['intercept'] -0) < .0001)
        self.assertEqual(result2['rank'], 2)
        
        self.assertTrue(abs(result3['slope'] -3) < .0001)
        self.assertTrue(abs(result3['intercept'] -4) < .0001)
        self.assertEqual(result3['rank'], 2)
        
        self.assertEqual(result4['rank'], 1)
        #test on real data
        data = self.testData[0]
        data = self.analysis.linearFitDataSeries(data)
        data = self.analysis.calculateRisiduals(data)
        self.assertTrue(abs(data.dataStats['slope'] - 0.041034923339) < 0.00000001)
        
    def test_dataLinReg(self):
        '''Test that analysis can process a dataSeries'''
        data = self.testData[0]
        data.dataPoints = [(x, x) for x in range(10)]
        data1 = self.analysis.linearFitDataSeries(data)
        
        self.assertTrue(abs(data1.dataStats['slope'] - 1.0) < .0000001)
        self.assertTrue(abs(data1.dataStats['intercept'] -0) < .0000001)
        self.assertEqual(data1.dataStats['rank'], 2)
        
    def test_calcRisiduals(self):
        '''Make sure we can find the risidual'''
        
        data1 = self.testData[0]
        data2 = self.testData[1]
        data2.dataPoints = [(x, x) for x in range(10)]
        data1 = self.analysis.linearFitDataSeries(data1)
        data1 = self.analysis.calculateRisiduals(data1)
        data2 = self.analysis.linearFitDataSeries(data2)
        data2 = self.analysis.calculateRisiduals(data2)
        
        self.assertTrue(abs(data1.dataStats['risidual'] - 0) < 0.00000001)
        
        self.assertTrue(abs(data2.dataStats['risidual'] - 0) < 0.00000001)
        

        
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
