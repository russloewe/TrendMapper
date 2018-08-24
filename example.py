from Analysis.data_interface import DataInterface
from Analysis.analysis import Analysis

def runner1():
    ''' Load a folder of CSV files, index, pull some data, save whole
    db to disk.
    by ommitting some steps this can be used to laod csv files into
    a sql database, with whatever indices '''
    #startup the interface
    interface = DataInterface()
    
    #specify the attributes that we are intersted in
    #names = ['DATE', 'STATION', 'TAVG', 'NAME', 'LATITUDE', 'LONGITUDE']
    names = ['DATE', 'STATION', 'DP10']
    interface.setAttributeNames(names)
    
    #start the memory sql database with attribute names that we set
    print 'Init SQL database'
    interface.initSQL()
    
    #load all the csv files into the sql database
    print 'Loading Folder'
    interface.loadFolder('./Analysis/test/testcsv/')
    
    #create a spacial index
    print 'Creating geometry index'
    #interface.createGeomIndex('geomindex', 'STATION', 'LONGITUDE', 'LATITUDE')
    
    #get a list of all the stations that got loaded into memory    
    print 'Pulling station list'
    stations = interface.pullUniqueKeys('STATION', tableName=interface.mainTableName)
    total = len(stations)
    print '{} stations'.format(total)
    
    print 'Creating index for stations'
    #interface.indexTable('stationIndex', interface.mainTableName, 'STATION')
    
    print 'Querrying stations'    
    c = 0
    for i in stations:
        c += 1
        if c % 100 == 0:
            print "{} out of {} pulled".format(c,total)
        interface.pullXYData('STATION', stations[0] ,'DATE','DP10')

    #save the database to disc
    print 'Saving database to disk'
    interface.saveMainConToDB('./Analysis/test/example2.db', overwrite=True)
   
   
def runner2():
    '''open plain sql databasa and add geo and station index'''
    #startup the interface
    interface = DataInterface()
    
    #specify the attributes that we are intersted in
    names = ['DATE', 'STATION', 'TAVG', 'NAME', 'LATITUDE', 'LONGITUDE']
    interface.setAttributeNames(names)
    
    #load all the csv files into the sql database
    print 'Connecting to database'
    interface.connectMainSQL('./Analysis/test/example0.db', tableName='CSVdata')

    #create a spacial index
    print 'Creating geometry index'
    interface.createGeomIndex('geomindex', 'STATION', 'LONGITUDE', 'LATITUDE')
    
    print 'Creating index for stations'
    interface.indexTable('stationIndex', interface.mainTableName, 'STATION')
   
   
def runner3():
    '''just copy the data and specified attributes from csv files 
    to a sql databasa without any indecies or spaitalite '''
    #startup the interface
    interface = DataInterface()
    
    #specify the attributes that we are intersted in
    names = ['DATE', 'STATION', 'TAVG', 'NAME', 'LATITUDE', 'LONGITUDE']
    interface.setAttributeNames(names)
    
    interface.initSQL(spatialite = False)
    
    #load all the csv files into the sql database
    print 'Loading Folder'
    interface.loadFolder('./Analysis/test/')

    #save the database to disc
    print 'Saving database to disk'
    interface.saveMainConToDB('./Analysis/test/example0.db', overwrite=True)
    
if __name__ == "__main__":
    import os
    import cProfile
    cProfile.run('runner2()')


