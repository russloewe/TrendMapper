from data_interface import DataInterface
from analysis import calculateLinearRegression, mean
'''to call the module functions from parent dir:'''
#from Analysis.data_interface import DataInterface
#from Analysis.analysis import calculateLinearRegression, mean
def runner1():
    ''' Load a folder of CSV files, index, save whole
    db to disk.'''
    #startup the interface
    interface = DataInterface()
    
    #specify the attributes that we are intersted in
    names = ['DATE', 'STATION', 'TAVG', 'NAME', 'LATITUDE', 'LONGITUDE']
    interface.setAttributeNames(names)
    
    #start the memory sql database with attribute names that we set
    print 'Init SQL database'
    interface.initSQL('', mainTableName = 'dataTable')
    
    #load all the csv files into the sql database
    print 'Loading Folder'
    interface.loadFolder('./test/')
    
    print 'Creating index for stations'
    interface.indexTable('stationIndex', 'dataTable', 'STATION')
    
    #create a spacial index
    print 'Creating geometry index'
    interface.createGeoTable('geoIndex', 'STATION', 'LONGITUDE', 'LATITUDE')
    
    #get a list of all the stations that got loaded into memory    
    print 'Pulling station list'
    stations = interface.pullUniqueKeys('STATION', 'dataTable')
    total = len(stations)
    print '{} stations'.format(total)
    
    #save the database to disc
    print 'Saving database to disk'
    interface.saveMainConToDB('./geodata.db', overwrite=True)

def runner2():
    '''just copy the data and specified attributes from csv files 
    to a sql databasa without any indecies or spaitalite. '''
    #startup the interface
    interface = DataInterface()
    
    #specify the attributes that we are intersted in
    names = ['DATE', 'STATION', 'TAVG', 'NAME', 'LATITUDE', 'LONGITUDE']
    interface.setAttributeNames(names)
    
    #create a new sql database in memory without spacialite metadata
    interface.initSQL('', mainTableName = 'dataTable', spatialite = False)
    
    #load all the csv files into the sql database
    print 'Loading Folder'
    interface.loadFolder('./test/')

    #save the database to disc
    print 'Saving database to disk'
    interface.saveMainConToDB('./plainout.db', overwrite=True)

def runner3():
    '''open plain sql database and add geo and station index.
    Outcome: existing database is modified'''
    #startup the interface
    interface = DataInterface()
    
    #specify the attributes that we are intersted in
    names = ['DATE', 'STATION', 'TAVG', 'NAME', 'LATITUDE', 'LONGITUDE']
    interface.setAttributeNames(names)
    
    #attach to the database created earlier
    print 'Connecting to database'
    interface.connectMainSQL('./plainout.db', mainTableName = 'dataTable')
    
    #Optional: move database to ram since creating the spatialite metadata takes 
    #way longer on the disk
    print 'Loading DB to memory'
    interface.saveMainConToDB(':memory:', attach = True)

    #create index
    print 'Creating index for stations'
    interface.indexTable('stationIndex', interface.mainTableName, 'STATION')
    
    #create a spacial index
    print 'Creating geometry index'
    interface.createGeoTable('geoIndex', 'STATION', 'LONGITUDE', 'LATITUDE', initSpatialite = True)
    
    #save back to disk
    print 'Saving Db to disk'
    interface.saveMainConToDB('./plainout_geoUpdated.db', overwrite = True)
    
def runner4():
    '''Load a geo database and get a list of the stations, then
    get a list of the stations that are inside the contigous us.'''
    
    #startup the interface
    interface = DataInterface()
    
    #specify the attributes that we are intersted in
    names = ['DATE', 'STATION', 'TAVG', 'NAME', 'LATITUDE', 'LONGITUDE']
    interface.setAttributeNames(names)
    
    #load all the csv files into the sql database
    print 'Connecting to database'
    interface.connectMainSQL('./geodata.db', mainTableName = 'dataTable')
    
    #get a list of all the stations in the geoindex that was created in
    #runner1    
    print 'Pulling station list'
    stations = interface.pullUniqueKeys('STATION', tableName = 'geoIndex')
    total = len(stations)
    print '{} stations'.format(total)
    
    print 'Selecting by location'
    interface.indexTable('stationIndex', interface.mainTableName, 'STATION')
    res = interface.filter('STATION', './test/states.sqlite', 'geoIndex', 'states', 'GEOMETRY' , 'GEOMETRY')
    print res
    print len(res)
    
def runner5():
    '''Total run through, load data, index, select by location, perform
    analysis, dump old data and tables and save spatialite layer ready
    for QGIS'''
    #startup the interface
    interface = DataInterface()
    
    #specify the attributes that we are intersted in and init a database in memory
    names = ['DATE', 'STATION', 'TAVG', 'NAME', 'LATITUDE', 'LONGITUDE']
    interface.setAttributeNames(names)
    interface.initSQL('')
    
    #load data from a folder of CSV files
    print 'Loading Folder'
    interface.loadFolder('./test/')
    
    #index the station column to speed up next steps
    print 'Creating index for stations'
    interface.indexTable('stationIndex', interface.mainTableName, 'STATION')
    
    #Creating geometry index
    interface.createGeoTable('geomindex', 'STATION', 'LONGITUDE', 'LATITUDE')

    #get a list of all the stations that are inside the contig USA   
    print 'Pulling station list'
    stations =  interface.filter('STATION', './test/states.sqlite', 'geomindex', 'states', 'GEOMETRY' , 'GEOMETRY')
    total = len(stations)
    print '{} stations'.format(total)
    
    #create new geo table with the stations inside contig USA
    print 'Creating new geotable'
    interface.createGeoTable('resulttable', 'STATION', 'LONGITUDE', 'LATITUDE', keySubset=stations)

    #calculate trend lines
    print 'running function'
    interface.applyFunction('STATION', stations, 'DATE', 'TAVG', 'resulttable', calculateLinearRegression) 

    print 'Dropping old tables'
    interface.dropTable('geomindex')
    interface.dropTable('metadata')
    interface.dropTable(interface.mainTableName)
    
    print 'Writing data to sql database on disk'
    interface.saveMainConToDB('./test/calculated_trends.db', overwrite=True)  
        
if __name__ == "__main__":
    import os
    import cProfile
    runner1()
    runner2()
    runner3()
    runner4()
    cProfile.run('runner5()')


