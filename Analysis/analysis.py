import csv
import numpy
from sets import Set
from datainterface import DataInterface

class Analysis():
    def __init__(self):
        '''The station dictionary uses the user inputted unique key as
           dictionary key, and the dict key points to an array of tuples
           which contain (x,y) data'''
        self.station_dictionary = {}  #init station dictionary
        '''linear outliers is a list of names of unique keys for statistical
        outliers, defalut 2 time std dev from mean. Init as None so we
        don't mistakenly think there are no outliers when we just haven't ran 
        the computation yet'''
        self.show_warnings = True
        self.skipped_datapoints = 0
        self.row_count = 0

    
    def set_unique_vale(self, uniquekey):
        '''setter for unique'''
        self.unk = uniquekey
        
    def set_independent_var(self, invar_key):
        '''setter for x var'''
        self.ink = invar_key
        
    def set_dependent_var(self, devar_key):
        '''setter for y var'''
        self.dek = devar_key
        
        
    def find_key_index(self, row):
        '''Takes array of the first line of CSV file and
            locates the indices of the three attribute columns
            we need for analysis'''
        self.name_index = row.index(self.unk)
        self.x_index = row.index(self.ink)
        self.y_index = row.index(self.dek)

    def add_data_point(self, row):
        '''The list from the CSV reader should be:
           row[self.name_index] = name
           row[self.x_index] = year
           row[self.y_index] = TAVG  
           *^format accurate as of 7/27/2018 but may change later 
                    
           Search for name in station_dictionay. If it is in there 
           append (year, TAVG) tuple to array indexed by name. If name is 
           not in station dictionay, add name:[(year,TAVG)] to dictionary
           
           For now cast both numbers to float '''
        
        if self.row_count == 0:
            #process first csv row for key indices
            self.find_key_index(row)
            return #first line proccess stops here 
            
        #grab the values from row befor proccessing
        
        try:
            x_val = float(row[self.x_index])
            y_val = float(row[self.y_index])
        except ValueError:
            self.skipped_datapoints += 1
            if self.show_warnings:
                print "Skipping row: "
                print row
            return
            
        name = row[self.name_index]
        if name not in self.station_dictionary:
            #self.station_dictionary[name] = {"data":[(x_val, y_val)]}
            self.initStation(name)
        self.station_dictionary[name]['data'].append((x_val, y_val))
    
    def initStation(self, name):
        '''setup the dictionaries that are used to store
        inforamtion about each station'''
        self.station_dictionary[name] = { 'name' : name,
                                          'data':[], 
                                          'linearfit':[],
                                          'meta':{'outlier': None}}

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
        return [slope, intercept, rank]
           

    def import_CSV(self, file_name):
        ''' basic wrapper function for csv reader. Uneccessary for now
            but might need abstration later'''
        with open(file_name, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            #reset counters before processing
            self.row_count = 0
            self.skipped_datapoint = 0 
            for row in spamreader:
                self.add_data_point(row)
                self.row_count += 1
        print "Loaded {} rows from {}".format(self.row_count, file_name)
        print "Skipped {} rows with unparsable data".format(self.skipped_datapoints)
        row_count = 0 #rest after done
        self.skipped_datapoints = 0

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
            
    def print_data(self):
        '''quickly show date was loaded to user'''
        for station in self.station_dictionary:
            print station, self.station_dictionary[station]
    
    def print_slopes(self):
        '''quickly test slope finder function for user'''
        for data in self.linear_results:
            print data
            
    def write_linear_fit_CSV(self, filename, export_risduals = True, write_CSVT = False, filter_outliers = False):
        '''write the calculated data to a CSV file'''
        line_counter = 0
        if filter_outliers is None:  #make sure we calculated outliers first
            raise ValueError("asked to filter outlier, but outlier hasn't been generated yet")
        
        with open(filename, 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
            #write header to first line, self.unk is original unique key
            if export_risduals:                
                spamwriter.writerow([self.unk, 'slope', 'intercept', 'risidual']) 
                for station in self.station_dictionary:
                    station = self.station_dictionary[station]
                    results = station['linearfit']
                    metaData = station['meta']
                    
                    spamwriter.writerow([station['name'], results[0], results[1], metaData['risiduals']])
                    line_counter += 1
            print "Wrote {} lines to {}".format(line_counter, filename)
            
            if write_CSVT:
                with open(filename+'t', 'w') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar=' ', quoting=csv.QUOTE_MINIMAL)
                    if export_risduals:
                        spamwriter.writerow(['"String"', '"Float"', '"Float"', '"Float"'])
                    else:
                        spamwriter.writerow(['"String"' , '"Float"', '"Float"'])

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
            
    def print_stations(self):
        for station in self.station_dictionary:
            print station,  self.station_dictionary[station]['linearfit'], self.station_dictionary[station]['meta']
            
    def addDataPoint(self, name, x_val, y_val):
        ''' adds data directly to the station dictoinay, automatically 
        grouping by name so that the calling function can choose to either add
        one group (aka station name) or just add everything at once'''
        if name not in self.station_dictionary:
            self.initStation(name)
        self.station_dictionary[name]['data'].append((x_val, y_val))

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
 





