import csv
import numpy
from sets import Set
#from Analysis.data_interface import DataInterface
from data_interface import DataInterface
class Analysis():
    def __init__(self):
        '''linear outliers is a list of names of unique keys for statistical
        outliers, defalut 2 time std dev from mean. Init as None so we
        don't mistakenly think there are no outliers when we just haven't ran 
        the computation yet'''
        self.show_warnings = True
        self.skipped_datapoints = 0
        self.row_count = 0
    
    def calculateLinearRegression(self, dataSet):
        '''take an array of tuples, [(x1,y1), (x2,y2) ..., (xn,yn)]
           reorganize as two arrays [x1, x2 ..., xn] and [y1, y2, ..., yn]
           and use numpy least squares to find linear best fit coeeficients and
           return the slope and intercept for the best fit line and rank'''
        x = [] #init independent var array
        y = [] #init dependent var array
        for data_point in dataSet:
            x_val,y_val = data_point  #unpack tuple
            x.append(x_val)
            y.append(y_val)
        if len(x) != len(y):
            print "something went wrong, x y dim missmath"
            return None
        A = numpy.vstack([x, numpy.ones(len(x))]).T
        linearFitResult = numpy.linalg.lstsq(A,y)
        slope, intercept = linearFitResult[0]
        rank = linearFitResult[2]
        results = {'slope' : slope, 'intercept': intercept, 'rank' : rank, 'setsize' : len(dataSet)}
        return(results)
           
    def linearFitDataSeries(self, dataSet):
        '''take the dataSeries object and run it through the regression
        function and put the result into the dataSeries attributes'''
        results = self.calculateLinearRegression(dataSet.dataPoints)
        for key in results:
            dataSet.addStat(key, results[key])
        return(dataSet)

            
    def calculatePopulationStats(self, dataArray, key):
        '''take the results from the linear calc, rearrange them to list
        of names and slopes. then find entries outside of threshold * standard
        deviation'''
        popSample = []
        for data in dataArray:
            popSample.append(data.dataStats[key])
        popMean = numpy.mean(popSample)
        popStd = numpy.std(popSample)
        
        for data in dataArray:
            keyVal = data.dataStats[key]
            
            zScore = (popMean - keyVal) / popStd
            sqrtN = numpy.sqrt(data.dataStats['setsize'])
            tScore = (popMean - keyVal) / (popStd / sqrtN)
            data.addStat('{}_zscore'.format(key) , zScore)
            data.addStat('{}_tscore'.format(key) , tScore)
            data.addStat('{}_mean'.format(key) , popMean)
            data.addStat('{}_std'.format(key) , popStd)
    
    def calculateRisiduals(self, dataSeries):
        '''Take a dataseries and calculate the difference in the real value
        for each year in the set with the value we get by using our linear model'''
        risidual = 0
        slope = dataSeries.dataStats['slope']
        intercept = dataSeries.dataStats['intercept']
        for dataPoint in dataSeries.dataPoints: 
            x, y = dataPoint
            risd = (x * slope + intercept) - y
            risidual += risd
        dataSeries.addStat('risidual', risidual)
        return(dataSeries)
            
def runner():
    interface = DataInterface()
    interface.loadFolder('./test/')
    interface.setCategoryLable('STATION')
    interface.setXLable('DATE')
    interface.setYLable('TAVG')
    interface.addCopyAttributeLable('LATITUDE')
    interface.addCopyAttributeLable('LONGITUDE')
    interface.indexCSVFiles()
    interface.indexCategories()
    testData = []
    stations = interface.getCategoryList()
    for station in stations:
        data = interface.getCategoryDataset(station)
        testData.append(data)
    
    analysis = Analysis()
    result1 = analysis.linearFitDataSeries(testData[0])
    result1 = analysis.calculateRisiduals(testData[0])
    print result1.dataStats['slope']
    print result1.dataStats['risidual']

    
if __name__ == "__main__":
    import os
    import cProfile
    cProfile.run('runner()')
    
   # d = DataInterface()
   # d.addCSVFile('1.csv')
   # d.addCSVFile('2.csv')
   # d.addCSVFile('3.csv')
    #d.addCSVFile('4.csv')

   # d.addCSVFile('s1.csv')
    #d.addCSVFile('s2.csv')
   # d.addCopyAttributeLable('LATITUDE')
   # d.name = 'STATION'
    #d.xLable = 'DATE'
   # d.yLable = 'TAVG'
    #d.indexCSVFiles()
    #for u in d.CSV:
      #  print u.name, u.indexDict
    
    #stations = d.getCSVNameList()
   # print stations
    #data = d.getCSVNameData(stations[0])
    #print data.name, data.dataPoints, data.copyAtttributes
    #print d.getCSVCount()
  
    if 1 == 2:
        analysis = Analysis( )  #TAVG_mtrix.csv
        analysis.set_unique_vale('STATION')
        analysis.set_independent_var('DATE')
        analysis.set_dependent_var('DX90') 
        analysis.show_warnings = False
        analysis.import_CSV('all.csv')
        analysis.calculate_linear_fit(discard_badfit = True)
        #analysis.print_slopes()
        analysis.find_outliers()
        analysis.computRegressionStats()
        analysis.write_linear_fit_CSV("all_TAVG.csv", export_risduals = True, write_CSVT = True, filter_outliers = True)
        analysis.computRegressionStats()
 





