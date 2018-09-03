import csv, sqlite3
import os
import logging
logging.getLogger(__name__)
FORMAT = '%(asctime)-15s:%(levelname)s: {}: %(message)s'.format(__name__)
logging.basicConfig(format=FORMAT, filename='{}.log'.format(__name__), level=logging.WARNING)
class DataInterface():
    
    def __init__(self):
        self.attributeNames = []
        self.mainTableName = None
        self.maincon = None
        
    def setAttributeNames(self, names):
        '''add attributes to an array that will be copied from 
        the input CSV to the SQL database'''
        logging.info('Function called: setAttributeNames("{}")'\
                                                        .format(names))
        for name in names:
            if name not in self.attributeNames:
                self.attributeNames.append(name)
        self.attributeNamesTuple = tuple(self.attributeNames)
    
    def getMainCur(self):
        '''Raise an error if there is no main database connection'''
        logging.info('Function call: checkMainCon()')
        if self.maincon == None:
            logging.error('Main connection is none')
            raise AttributeError('No main database connection')
        try:
            cur = self.maincon.cursor()
        except AttributeError:
            logging.error('Could not get cursor for main database')
            raise AttributeError('Could not get cursor for main DB')
        return cur
            
    def initSQL(self, path, spatialite=True, overwrite=False, 
                connect=True, mainTableName='CSVdata'):
        '''set up our initial tmp sql database in memory and init some 
        tables maintable: the name to load the incomming dataset, ie, 
        the csv outtable:   the name for the table where well put the
        results of the analysis meta table: name of files that have 
         been loaded to prevent loading a file twice'''
        logging.info('Function call: initSQL("{}", spatialite={},'\
                      'overwrite={}, connect={}, mainTableName="{}")'\
                      .format(path, spatialite, overwrite, connect, 
                      mainTableName))
        if len(self.attributeNames) < 1:
            logging.error("No attributes specified, cant init SQL")
            raise AttributeError('No attributes specified, cant init'\
                                 ' SQL')
        if overwrite:
            eraseFile(path)
        elif os.path.isfile(path):
            logging.error('File: "{}" exists and overwrite is False'\
                          .format(path))
            raise IOError('File: "{}" exists and overwrite is False'\
                          .format(path))
        newdb = spatialite_connect(path)
        cur = newdb.cursor()
        if spatialite:
            logging.info('Initializing Spatialite metadata for "{}".'\
                         .format(path))
            cur.execute('SELECT InitSpatialMetadata()')
        cur.execute("CREATE TABLE {} (ID int PRIMARY KEY)"\
                    .format(mainTableName) )
        cur.execute('CREATE TABLE metadata (filename VARCHAR(200)'\
                    ' UNIQUE)')
        for name in self.attributeNames:
            cur.execute("ALTER TABLE {} ADD {} VARCHAR(50)"\
                        .format(mainTableName, name))
        newdb.commit()
        if connect:
            logging.info('Setting "{}" as main DB connection'\
                         .format(path))
            logging.info('Setting "{}" as main data table'
                         .format(mainTableName))
            self.maincon = newdb
            self.mainTableName = mainTableName
   
    def createGeoTable(self, tableName, uniqueKey, xName, yName,
                       keySubset=None, initSpatialite=False):
        '''create a new table with a geometry point layer for 
        querrying by location

        plan- create new table, leave lat lon  cols'''
        logging.info('Function call: creatGeoTable("{}", "{}", "{}", '\
                       '"{}", keySubset={}, initSpatialite={})'.format(
                     tableName, uniqueKey, xName, yName, keySubset,
                     initSpatialite))
        cur = self.getMainCur()
        #make sure the input table is good
        if self.mainTableName is None:
            logging.error('No main table specified, cannot create' \
                                                       'geo table')
            raise AttributeError('No main table specified')
        if self.mainTableName not in self.getTables():
            logging.error('No table "{}" in main database, cannot '\
                      'create geo table.'.format(self.mainTableName))
            raise AttributeError('No table "{}" in main'\
                            'database'.format(self.mainTableName))
        try:
            cur.execute('CREATE TABLE {} ({} VARCHAR(50), {} FLOAT, '\
                        '{} FLOAT)'.format(tableName, uniqueKey,
                                           xName, yName))
        except sqlite3.OperationalError as e:
            logging.error('Unable to create table: "{}"'.format(
                          tableName), exc_info=True)
            raise e
        #init spaital lite or pass if it already has metadata
        if initSpatialite:
            logging.info('Initializing Spatialite metadata for "{}".'\
                         .format(tableName))
            cur.execute('SELECT InitSpatialMetadata()')
        sql = "SELECT AddGeometryColumn('{}', 'GEOMETRY', 4326, "\
              "'POINT', 'XY');".format(tableName)
        cur.execute(sql)
        
        if keySubset == None:
            keyList = self.pullUniqueKeys(uniqueKey)
        else:
            keyList = keySubset
       
        for k in keyList:
            cur.execute("SELECT {}, {}, {} FROM {} WHERE {} == '{}' "\
                        "LIMIT 1;".format(uniqueKey, xName, yName,
                                     self.mainTableName, uniqueKey, k))
            result = cur.fetchone()
            name = result[0]
            geom = "GeomFromText('POINT({} {})', 4326)".format(
                                        str(result[1]), str(result[2]))
            params = (tableName, uniqueKey, 'GEOMETRY', name, geom )
            sql = "INSERT INTO {} ({}, 'GEOMETRY') VALUES ('{}', {})"\
                            .format(tableName, uniqueKey, name, geom)
            cur.execute(sql)
        self.maincon.commit()
        
    def getTables(self):
        '''Get a list of table from the main database'''
        logging.info('Function call: getTables()')
        cur = self.getMainCur()
        sql = "SELECT name FROM sqlite_master WHERE type='table' ;"
        cur.execute(sql)
        results = [str(i[0]) for i in cur.fetchall()]
        logging.info('Tables found in main DB: "{}"'.format(results))
        return(results)
        
    def getTableAttributes(self, tableName):
        '''Get a list of the attribute columns in a table'''
        logging.info('Function call: getTableAttributes("{}")'.format(
                                                    tableName))
        cur = self.getMainCur()
        cur.execute('PRAGMA table_info({})'.format(tableName))
        columns = [i[1] for i in cur.fetchall()]
        return(columns)
        
        
    def connectMainSQL(self, path, mainTableName=None):
        '''make a connection to a database on the disk'''
        logging.info('Function call: connectMainSQL("{}",'\
                    ' mainTableName={})'.format(path, mainTableName))
        if not os.path.isfile(path):
            logging.error('No file "{}" found on disk'.format(path))
            raise IOError('No file "{}" found on disk'.format(path))
        if mainTableName == None:
            if self.mainTableName == None:
                logging.error('Cannot connect to database without '\
                                               'a main table specified')
                raise AttributeError('Cannot connect to database'\
                                     ' without a main table specified')
            mainTableName = self.mainTableName
        else:
            self.mainTableName = mainTableName
        #dont set the new connection as the main connection until
        #we are sure that the database will work
        tmp = spatialite_connect(path)
        cur = tmp.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        result = [str(i[0]) for i in cur.fetchall()]
        
        #make sure the database we connect to is not empty and has the 
        #right table
        if (result is None) or (len(result) < 1):
            logging.error('No tables in "{}".'.format(path))
            raise AttributeError('No tables in "{}".'.format(path))
        if (mainTableName not in result):
            logging.error('Table "{}" not in "{}".'\
                                        .format(mainTableName, path))
            raise AttributeError('Table "{}" not in "{}".'\
                                         .format(mainTableName, path))
        
        #make sure the main table in the database has the columns
        # we need
        cur.execute('PRAGMA table_info({})'.format(mainTableName))
        columns = [i[1] for i in cur.fetchall()]
        for attr in self.attributeNames:
            if attr not in columns:
                self.maincon = None
                raise AttributeError('Attribute {} not in'\
                   ' table {} in {}'.format(attr, mainTableName, path))
        self.maincon = tmp
        
        
    def loadCSV(self, filePath):
        '''take the path of a csv file and import the rows into a sql 
        database'''
        logging.info('Loading file: "{}"'.format(filePath))
        cur = self.getMainCur()
        try:
            #if the file has been loaded, skip
            cur.execute('INSERT INTO metadata (filename) VALUES (?)',
                                                           (filePath,))
        except sqlite3.IntegrityError:
            logging.warning('File "{}" already loaded to DB'\
                                .format(filePath))
            return False
        
        with open(filePath, 'rb') as csvfile:
            dr = csv.DictReader(csvfile) # comma is default delimiter
            for i in dr:
                to_db = []
                try:
                    for name in self.attributeNames:
                        to_db.append(i[name])
                except KeyError:
                    #tell the calling function that the file cant load
                    return False
                sqlVals = tuple(to_db)
                sqlStatement = "INSERT INTO {} {} VALUES {};"\
                                           .format(self.mainTableName,
                                    self.attributeNamesTuple, sqlVals)
                cur.execute(sqlStatement)
        self.maincon.commit()
        return True
    
    def writeTableToCSV(self, path, tableName):
        cur = self.getMainCur()
        with open(path, 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
            #write header to first line, self.unk is original unique key
            cur.execute('PRAGMA table_info({})'.format(tableName))
            columns = [i[1] for i in cur.fetchall()]
            # header = [f for f in self.dataSets[0].dataStats]          
            spamwriter.writerow(columns) 
            cur.execute('SELECT * FROM {}'.format(tableName))
            for data in cur.fetchall():
                #row = [data.dataStats[key] for key in header]
                spamwriter.writerow(data) 
    
    def loadFolder(self, folderPath):
        '''Get a list of csv files in the provided directory and
            add each file with the addCsvFile function'''
        for file in os.listdir(folderPath):
            if file.endswith(".csv"):
                self.loadCSV(os.path.join(folderPath, file))
            
    def pullUniqueKeys(self, column, tableName=None, indexName=None):
        ''' grab a list of all the unique names in the given
        column'''
        logging.info('Function call: pullUniqueKeys("{}", '\
                     'tableName={}, indexName={})'.format(column,
                                                tableName, indexName))
        if tableName is None:
            tableName = self.mainTableName
            logging.info('Using table name: "{}"'.format(
                                                    self.mainTableName))
        cur = self.getMainCur()
        if indexName is not None:
            cur.execute('SELECT DISTINCT {} from {} INDEXED BY {}'\
                                   .format(column,tableName, indexName))
        else:
            cur.execute('SELECT DISTINCT {} from {}'.format(column, 
                                                        tableName))
        result = [ str(list(i)[0]) for i in cur.fetchall()]
        return result
        
    def pullXYData(self, keyCol, keyName, xName, yName, 
                                tableName=None, indexName=None):
        '''Get data set for specific keyname'''
        logging.info('Function call: pullXYData("{}", "{}", "{}", '\
                            '"{}", tableName={}, indexName={})'.format(
                            keyCol, keyName, xName, yName, tableName,
                                                       indexName))
        data = []
        cur = self.getMainCur()
        if tableName is None:
            tableName = self.mainTableName
            logging.info('Using table name: "{}"'.format(
                                                    self.mainTableName))
        if indexName is not None:
            cur.execute('SELECT {}, {} FROM {} INDEXED BY {} '\
                    'WHERE {} == "{}"'.format(xName, yName, tableName,
                                        indexName, keyCol, keyName))
        else:
            cur.execute('SELECT {}, {} FROM {} WHERE {} == "{}"'\
                                    .format(xName, yName, tableName,
                                         keyCol, keyName))
        for row in cur:
            if (row[0] == '') or  (row[1] == ''):
                pass
            else:
                x = float(row[0])
                y = float(row[1])
                data.append((x, y))
        return data
        
    def saveMainConToDB(self, path, attach=False, overwrite=False):
        '''save the main data table 'CSVdata' to SQL db on disk, 
        takes filename'''
        logging.info('Function call: saveMainConToDB("{}", attach={},'\
                        'overwrite={})'.format(path, attach, overwrite))
        if overwrite:
            eraseFile(path)
        newdb = spatialite_connect(path)
        query = "".join(line for line in self.maincon.iterdump())
        try:
            newdb.executescript(query)
        except sqlite3.OperationalError as e:
            logging.error('Unable to dump database: {}. {} might'\
                              ' already exist.'.format(str(e), path))
            raise e
        newdb.commit()
        if attach:
            self.maincon = newdb
        return newdb

    def indexTable(self, indexName, tableName, indexCol):
        '''index the main database'''
        cur = self.getMainCur()
        try:
            cur.execute('CREATE INDEX {} ON {}({})'.format(indexName,
                                                tableName, indexCol))
        except sqlite3.OperationalError as e:
            logging.warning('Could not create index', exc_info = True)
        self.maincon.commit()

    def close(self):
        '''close the db connection'''
        logging.info('Closing main database connection')
        if self.maincon == None:
            logging.warning('Error, no main database connection')
        else:
            self.maincon.close()
    def attachDB(self, path, name):
        '''Attach a database'''
        cur = self.getMainCur()
        sql = "ATTACH DATABASE '{}' AS '{}'".format(path, name)
        cur.execute(sql)
        self.maincon.commit()
        
    def detachDB(self, name):
        '''detach the database'''
        cur = self.getMainCur()
        sql = "DETACH {}".format(name)
        cur.execute(sql)
        self.maincon.commit()
        
    def dropTable(self, tableName):
        '''simple table drop'''
        logging.info('Function call: dropTable("{}")'.format(tableName))
        cur = self.getMainCur()
        cur.execute('DROP TABLE {}'.format(tableName))
        
    def filter(self, srcCol, path, srcTable, maskTable, srcGeoCol, 
                                                    maskGeoCol):
        '''column is the name of the column to return on a match'''
        logging.info('Function call: filter("{}", "{}", "{}", "{}",'\
                    ' "{}", "{}")'.format(srcCol, path, srcTable, 
                                      maskTable, srcGeoCol, maskGeoCol))
        cur = self.getMainCur()        
        self.attachDB(path, 'db')
        try:
            cur.execute('SELECT db.{}.{} FROM db.{}'.format(maskTable, 
                                            maskGeoCol, maskTable) )
        except sqlite3.OperationalError as e:
            logging.critical('Failed to attach database "{}": table'\
                            ' querry failed: "{}"'.format(path, str(e)))
            raise sqlite3.OperationalError('Database {} attach '\
                                    'failed: "{}"'.format(path, str(e)))
        
        #use spatialindex for querry. diff on gsoy set 100s down to 75s
        sql = "SELECT {} ".format(srcCol)
        sql += "FROM {} AS s, db.{} AS m ".format(srcTable, maskTable)
        sql += "WHERE Within(s.{}, m.{}) = 1 ".format( srcGeoCol,
                                                            maskGeoCol)
        sql += "AND m.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE " 
        sql += "f_table_name = 'DB=db.{}' AND search_frame = m.{})"\
                                         .format(maskTable, maskGeoCol)
        cur.execute(sql)
        
        result = [ str(list(i)[0]) for i in cur.fetchall()]
        self.detachDB('db')
        self.maincon.commit
        return result
    
    def applyFunction(self, keyCol, keySet, xLable, yLable, 
                                                outputTable, function):
        '''Get the data for the entries in the teySet list. 
        keyCol is the name for the column that keySet is querried,
        xLable, yLable is the cols to pull data,
        outputTable, outputCol is what sql table and col to park the 
        results function is the function to apply to each dataset
        '''
        cur = self.getMainCur()        
        #create a column for the result, process the first data entry
        #to get the dictionary keys to put in the table        
        data = self.pullXYData(keyCol, keySet[0], xLable, yLable)
        result = function(data)
        for keyName in result:
            sql = "ALTER TABLE {} ADD {} FLOAT".format(outputTable, 
                                                            keyName)
            cur.execute(sql)
        
        #now pull the data for real
        for key in keySet:
            data = self.pullXYData(keyCol, key, xLable, yLable)
            result = function(data)
            for item in result:
                sql = "UPDATE {} SET {} = {} WHERE {} = '{}'"\
                .format(outputTable, item, result[item], keyCol, key)
                cur.execute(sql)    
        self.maincon.commit()

def eraseFile(path):
    '''Remove a file if it exists'''
    logging.info('Function called: eraseFile("{}")'.format(path))
    try:
        os.remove(path)
    except:
        logging.warning('Exception trying to remove file', 
                                                         exc_info=True)
    if os.path.isfile(path):
        logging.error("Could not remove '{}' from disk".format(path))
        raise IOError("Could not remove '{}' from disk".format(path))
    else:
        logging.info('File: "{}" removed'.format(path))
        
'''the following function is taken from 
https://github.com/qgis/QGIS 
file QGIS/python/utils.py 592-620
Falls under the same GPL license as this project'''

def spatialite_connect(*args, **kwargs):
    """returns a dbapi2.Connection to a SpatiaLite db
    using the "mod_spatialite" extension (python3)"""
    con = sqlite3.dbapi2.connect(*args, **kwargs)
    con.enable_load_extension(True)
    cur = con.cursor()
    libs = [
        # SpatiaLite >= 4.2 and Sqlite >= 3.7.17, should work on all platforms
        ("mod_spatialite", "sqlite3_modspatialite_init"),
        # SpatiaLite >= 4.2 and Sqlite < 3.7.17 (Travis)
        ("mod_spatialite.so", "sqlite3_modspatialite_init"),
        # SpatiaLite < 4.2 (linux)
        ("libspatialite.so", "sqlite3_extension_init")
    ]
    found = False
    for lib, entry_point in libs:
        try:
            cur.execute("select load_extension('{}', '{}')".format(lib, entry_point))
        except sqlite3.OperationalError:
            continue
        else:
            found = True
            break
    if not found:
        raise RuntimeError("Cannot find any suitable spatialite module")
    cur.close()
    con.enable_load_extension(False)
    return con
