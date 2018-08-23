from Analysis.data_interface import DataInterface
from Analysis.analysis import Analysis

def runner():
    interface = DataInterface()
    names = ['DATE', 'STATION', 'TAVG', 'NAME', 'LATITUDE', 'LONGITUDE']
    interface.setAttributeNames(names)
    interface.initSQL()
    interface.loadFolder('./Analysis/test/')
    for i in interface.pullUniqueKeys('STATION'):
        print i
    #print len(interface.pullUniqueKeys('STATION'))
    
if __name__ == "__main__":
    import os
    import cProfile
    cProfile.run('runner()')


