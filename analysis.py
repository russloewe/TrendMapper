# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TrendMapperDialog
                                 A QGIS plugin
 calculate trendlines along catagories
                             -------------------
        begin                : 2018-07-28
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Russell Loewe
        email                : russloewe@gmai.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import csv
import numpy
from sets import Set

def calculateLinearRegression(x, y, includeStats=False):
    '''take an array of tuples, [(x1,y1), (x2,y2) ..., (xn,yn)]
       reorganize as two arrays [x1, x2 ..., xn] and [y1, y2, ..., yn]
       and use numpy least squares to find linear best fit coeeficients and
       return the slope and intercept for the best fit line and rank'''
    A = numpy.vstack([x, numpy.ones(len(x))]).T
    linearFitResult = numpy.linalg.lstsq(A,y)
    slope, intercept = linearFitResult[0]
    if includeStats:
        rank = linearFitResult[2]
        risidualSum = calculateRisidualSum(zip(x,y) ,slope , intercept)
        results = {'slope' : float(slope), 'intercept': float(intercept),
         'rank' : float(rank), 'risidualSum': float(risidualSum),
          'setsize' : len(x)}
    else:
         results = {'slope' : float(slope), 'intercept': float(intercept)}
    return(results)

def mean(data):
    if len(data) < 1:
        raise ValueError('No data points in dataset') 
    a = numpy.mean(data)
    results = {'mean' : a}
    return(results)
    
    
def calculateRisidualSum(dataSet, slope, intercept):
    '''Take a dataseries and calculate the difference in the real value
    for each year in the set with the value we get by using our linear model'''
    risidual = 0
    for dataPoint in dataSet: 
        x, y = dataPoint
        risd = (x * slope + intercept) - y
        risidual += risd
    return(risidual)

