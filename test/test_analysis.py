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

from analysis import *


class AnalysisTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.testData = [
                [[x for x in range(10)], [x for x in range(10)]],
            [[x for x in range(-10,10)], [x*2 for x in range(-10,10)]],
                [[x for x in range(10)], [ x*3+4 for x in range(10)]],
                [[1],[1]]
                         ]
        
    
    def test_linearRegression(self):
        '''Test that linear regression passes some test calculation'''
        result0 = calculateLinearRegression(self.testData[0][0], self.testData[0][1], includeStats = True)
        result1 = calculateLinearRegression(self.testData[1][0], self.testData[1][1], includeStats = True)
        result2 = calculateLinearRegression(self.testData[2][0], self.testData[2][1], includeStats = True)
        result3 = calculateLinearRegression(self.testData[3][0], self.testData[3][1], includeStats = True)
        
        self.assertTrue(abs(result0['slope'] - 1.0) < .0000001)
        self.assertTrue(abs(result0['intercept'] -0) < .0000001)
        self.assertTrue(abs(result0['risidualSum'] -0) < .0000001)
        self.assertEqual(result0['rank'], 2)
        
        self.assertTrue(abs(result1['slope'] -2) < .0001)
        self.assertTrue(abs(result1['intercept'] -0) < .0001)
        self.assertTrue(abs(result1['risidualSum'] -0) < .0000001)
        self.assertEqual(result1['rank'], 2)
        
        self.assertTrue(abs(result2['slope'] -3) < .0001)
        self.assertTrue(abs(result2['intercept'] -4) < .0001)
        self.assertTrue(abs(result2['risidualSum'] -0) < .0000001)
        self.assertEqual(result2['rank'], 2)
    
    def test_rank(self):
        '''Make sure that right rank is returned'''
        result = calculateLinearRegression(self.testData[3][0], self.testData[3][1], includeStats = True)
        self.assertEqual(result['rank'], 1)
        
    def test_linStats(self):
        '''make sure that stats are not returned for default params'''
        
        result0 = calculateLinearRegression(self.testData[3][0], self.testData[3][1])
        self.assertTrue('rank' not in result0)
    
    def test_calcRisiduals(self):
        '''Make sure we can find the risidual'''
        
        data0 = zip(self.testData[0][0], self.testData[0][1])
        data1 = zip(self.testData[1][0], self.testData[1][1])
        data2 = zip(self.testData[2][0], self.testData[2][1])
        data0Ris = calculateRisidualSum(data0, 1, 0)
        data1Ris = calculateRisidualSum(data1, 2, 0)
        data2Ris = calculateRisidualSum(data2, 3, 4)
        self.assertTrue(abs(data0Ris - 0) < 0.00000001)
        self.assertTrue(abs(data1Ris - 0) < 0.00000001)
        self.assertTrue(abs(data2Ris - 0) < 0.00000001)

    def test_mean(self):
        '''Make sure we can find the mean for a dataset'''
        data0 = self.testData[0][1]
        data1 = self.testData[1][1]
        data2 = self.testData[2][1]
        
        result0 = mean(data0)
        result1 = mean(data1)
        result2 = mean(data2)
        
        self.assertEqual(result0['mean'], 4.5)
        self.assertEqual(result1['mean'], -1)
        self.assertEqual(result2['mean'], 17.5)
        
    def tearDown(self):
        """Runs after each test."""
        self.interface = None
        

        


if __name__ == "__main__":
    suite = unittest.makeSuite(AnalysisTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
