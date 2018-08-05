import csv
import numpy
from sets import Set
from Analysis.data_interface import DataInterface
 
class Analysis():
    def __init__(self):
        '''linear outliers is a list of names of unique keys for statistical
        outliers, defalut 2 time std dev from mean. Init as None so we
        don't mistakenly think there are no outliers when we just haven't ran 
        the computation yet'''
        self.show_warnings = True
        self.skipped_datapoints = 0
        self.row_count = 0
    
    def find_linear_slope(self, station_data):
        '''take an array of tuples, [(x1,y1), (x2,y2) ..., (xn,yn)]
           reorganize as two arrays [x1, x2 ..., xn] and [y1, y2, ..., yn]
           and use numpy polyfit to find linear best fit coeeficients and
           return the first one which is slope, aka rate of change.
           BTW, numpy doesn't care about point order'''
        numpy.seterr(all='raise') #see if we can catch warnings
        x = [] #init independent var array
        y = [] #init dependent var array
        for data_point in station_data:
            x_val,y_val = data_point  #unpack tuple
            x.append(x_val)
            y.append(y_val)
        if len(x) != len(y):
            print "something went wrong, x y dim missmath"
            return None
        try:
            A = numpy.vstack([x, numpy.ones(len(x))]).T
            linear_fit = numpy.linalg.lstsq(A,y)
            print linear_fit
        except Warning:
            print "rank error"
        return linear_fit
        
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
        try:
            A = numpy.vstack([x, numpy.ones(len(x))]).T
            linearFitResult = numpy.linalg.lstsq(A,y)
            print linearFitResult
        except Warning:
            print "rank error"
        slope, intercept = linearFitResult[0]
        rank = linearFitResult[2]
        results = {'slope' : slope, 'intercept': intercept, 'rank' : rank}
        return(results)
           


    def calculate_linear_fit(self, discard_badfit = True):
        ''' call the linear fit equation and add name and results
            to array as subarry. Subarray was chosen to make writing to
            CSV easier'''
        self.linear_results = [] #start with empty list
        for station in self.station_dictionary:
            linear = self.find_linear_slope(self.station_dictionary[station]['data'])
            m, c = linear[0] # get slope and intercept respectivly
            r = linear[1] # get risdual
            if len(r) == 0:  # need to handle when numpy gives empty risudal
                r = ['']
            rank = linear[2] # get rank
            if rank < 2:
                print "Rank < 2 for {}, likely bad fit".format(station)
            if discard_badfit and rank < 2:
                print "skipping {}".format(station)
                pass
            total_points = len(self.station_dictionary[station])
            try:
                risidual_avg = float(r[0])/total_points
            except ValueError:
                risidual_avg = ' '
            self.station_dictionary[station]['linearfit'] = [m,c]
            #self.linear_results.append([station, m, c, r[0]])
            
    def find_outliers(self, threshold=2):
        '''take the results from the linear calc, rearrange them to list
        of names and slopes. then find entries outside of threshold * standard
        deviation'''
        names = []
        vals = []
        outlier_count = 0
        for station in self.station_dictionary:
            names.append(station) #names in first slot
            vals.append(self.station_dictionary[station]['linearfit'][0])  #slope of linreg in second slot
        if len(names) != len(vals):
            raise ValueError("names and values not same length")
        #find mean and standard deviation
        mean = numpy.mean(vals)
        std_dev = numpy.std(vals)
        #iterate again through looking for outliers
        for station in self.station_dictionary:
            value = self.station_dictionary[station]['linearfit'][0]
            if abs(value - mean) > std_dev*threshold :
                self.station_dictionary[station]['meta']['outlier'] = True
                outlier_count += 1
            else:
                self.station_dictionary[station]['meta']['outlier'] = False
        print "Found {} outliers {} std devs from mean".format(outlier_count, threshold)
        print "    mean: {}, std dev: {}".format(mean, std_dev)
    
    def computRegressionStats(self):
        '''comput varies statistics for the stations. EG, risidual sum for 
        the linear fit, the number of total points.. whatever else I want. 
        This will be put in the meta data dictionary which is an element for 
        the station dictionary'''
        for station in self.station_dictionary:
            risidual = 0
            slope = self.station_dictionary[station]['linearfit'][0]
            intercept = self.station_dictionary[station]['linearfit'][1]
            data_count = 0
            for data_point in self.station_dictionary[station]['data']:
                year, val = data_point
                calc_val = year * slope + intercept
                risidual += val-calc_val
                data_count += 1
            self.station_dictionary[station]['meta']['risiduals'] = risidual
            self.station_dictionary[station]['meta']['count'] = data_count
            
def runner():
    d = DataInterface()
    direct = "/home/russell/GIS/Data/station_year_summary/"
    count = 0
    print 'adding filenames '
    for file in os.listdir(direct):
        if count < 80000:
            if file.endswith(".csv"):
                d.addCSVFile(os.path.join(direct, file))
                count += 1
        else:
            break
    print 'indexing files'
    d.name = 'STATION'
    d.xLable = 'DATE'
    d.yLable = 'TAVG'
    d.addCopyAttributeLable('LATITUDE')
    d.indexCSVFiles()
    print d.getCSVCount()
    print 'generating station list'
    stations = d.getCSVNameList()
    print '{} valid stations found'.format(len(stations))
    print 'getting data for station {}'.format(stations[:1])
    data = d.getCSVNameData(stations[5])
    print data.name, data.copyAtttributes, data.dataPoints
    
    
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
 





