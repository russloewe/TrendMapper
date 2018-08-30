import csv
import numpy
from sets import Set

def calculateLinearRegression(dataSet, includeStats=False):
    '''take an array of tuples, [(x1,y1), (x2,y2) ..., (xn,yn)]
       reorganize as two arrays [x1, x2 ..., xn] and [y1, y2, ..., yn]
       and use numpy least squares to find linear best fit coeeficients and
       return the slope and intercept for the best fit line and rank'''
    x = [] #init independent var array
    y = [] #init dependent var array
    if len(dataSet) < 1:
        raise ValueError('No data points in dataset') 
    for data_point in dataSet:
        x_val,y_val = data_point  #unpack tuple
        x.append(x_val)
        y.append(y_val)
    if len(x) != len(y):
        raise ValueError('Dimension mismatch on x,y series')
    A = numpy.vstack([x, numpy.ones(len(x))]).T
    linearFitResult = numpy.linalg.lstsq(A,y)
    slope, intercept = linearFitResult[0]
    if includeStats:
        rank = linearFitResult[2]
        risidualSum = calculateRisidualSum(dataSet,slope , intercept)
        results = {'slope' : slope, 'intercept': intercept, 'rank' : rank, 'risidualSum': risidualSum, 'setsize' : len(dataSet)}
    else:
         results = {'slope' : slope, 'intercept': intercept}
    return(results)

def mean(data):
    x = [] #init independent var array
    y = [] #init dependent var array
    if len(data) < 1:
        raise ValueError('No data points in dataset') 
    for data_point in data:
        x_val,y_val = data_point  #unpack tuple
        x.append(x_val)
        y.append(y_val)
    if len(x) != len(y):
        raise ValueError('Dimension mismatch on x,y series')
    a = numpy.mean(y)
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

    
if __name__ == "__main__":
    pass
