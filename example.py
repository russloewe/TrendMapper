from Analysis.data_interface import DataInterface
from Analysis.analysis import Analysis

def runner():
    #startup the interface
    interface = DataInterface()
    #specify the attributes that we are intersted in
    names = ['DATE', 'STATION', 'TAVG', 'NAME', 'LATITUDE', 'LONGITUDE']
    interface.setAttributeNames(names)
    #start the memory sql database with attribute names that we set
    interface.initSQL()
    #load all the csv files into the sql database
    interface.loadFolder('./Analysis/test/')
    #interface.connectSQL('dbout.sqlite')
    #get a list of all the stations that got loaded into memory
    stations = interface.pullUniqueKeys('STATION')
    print len(stations)
    print stations[0]
    station = stations[2]
    print station
    data = interface.pullXYData('STATION', stations[0] ,'DATE','TAVG')
    print data
    interface.saveMainToDB('dbout2.sqlite', overwrite=True)
    interface.saveResultsToDB('dbout2.sqlite', overwrite=True)
    data = interface.pullXYData('STATION', 'USR0000WALD', 'DATE', 'TAVG')
    print data
    
if __name__ == "__main__":
    import os
    import cProfile
    cProfile.run('runner()')


