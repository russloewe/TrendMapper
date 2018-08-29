import csv, sqlite3
import os
import logging
logging.getLogger(__name__)
FORMAT = '%(asctime)-15s {}: %(message)s'.format(__name__)
logging.basicConfig(format=FORMAT, filename='{}.log'.format(__name__))
class DataInterface():
    
    def __init__(self):
        self.attributeNames = []
        self.mainTableName = None
        self.outTableName = None
        
    def setAttributeNames(self, names):
        '''add attributes to an array that will be copied from 
        the input CSV to the SQL database'''
        for name in names:
            if name not in self.attributeNames:
                self.attributeNames.append(name)
        self.attributeNamesTuple = tuple(self.attributeNames)
            
    def initSQL(self, path, spatialite=True, overwrite=False, connect=True, mainTableName='CSVdata'):
        '''set up our initial tmp sql database in memory and init some tables
        maintable: the name to load the incomming dataset, ie, the csv 
        outtable:   the name for the table where well put the results of the analysis
        meta table: name of files that have been loaded to prevent loading a file twice'''
        if len(self.attributeNames) < 1:
            raise AttributeError("no attributes specified, cant init SQL")
        if overwrite:
            try:
                os.remove(path)
            except:
                pass
            
        self.mainTableName = 'CSVdata'
        newdb = spatialite_connect(path)
        cur = newdb.cursor()
        
        if spatialite:
            
            cur.execute('SELECT InitSpatialMetadata()')
            
        cur.execute("CREATE TABLE {} (ID int PRIMARY KEY)".format(self.mainTableName) )
        cur.execute("CREATE TABLE metadata (filename VARCHAR(200) UNIQUE)")
        for name in self.attributeNames:
            cur.execute("ALTER TABLE CSVdata ADD {} VARCHAR(50)".format(name))
        newdb.commit()
        if connect:
            self.maincon = newdb
            self.mainTableName = mainTableName
   
    def createGeoTable(self, indexName, uniqueKey, xName, yName, keySubset=None, initSpatialite=False):
        '''create a new table with a geometry point layer for 
        querrying by location
        
        
        plan- create new table, leave lat lon  cols'''
        try:
            cur = self.maincon.cursor()
        except AttributeError:
            raise AttributeError('SQL connection not established')
        try:
            cur.execute('CREATE TABLE {} ({} VARCHAR(50))'.format(indexName, uniqueKey))
        except sqlite3.OperationalError as e:
            if str(e) == 'table {} already exists'.format(indexName):
                return
            else:
                raise sqlite3.OperationalError(str(e))

        #init spaital lite or pass if it already has metadata
        if initSpatialite:
            cur.execute('SELECT InitSpatialMetadata()')            
        
        sql = "SELECT AddGeometryColumn('{}', 'geom', 4326, 'POINT', 'XY');".format(indexName)
        cur.execute(sql)
        
        if keySubset == None:
            keyList = self.pullUniqueKeys(uniqueKey)
        else:
            keyList = keySubset
       
        for k in keyList:
            cur.execute("SELECT {}, {}, {} FROM {} WHERE {} == '{}' LIMIT 1;".format(uniqueKey, xName, yName, self.mainTableName, uniqueKey, k))
            result = cur.fetchone()
            name = result[0]
            geom = "GeomFromText('POINT({} {})', 4326)".format(str(result[1]), str(result[2]))
            params = (indexName, uniqueKey, 'geom', name, geom )
            sql = "INSERT INTO {} ({}, geom) VALUES ('{}', {})".format(indexName, uniqueKey, name, geom)
            cur.execute(sql)
        self.maincon.commit()

    def close(self):
        '''close the sql connection'''
        self.maincon.close()
        self.maincon = None
    
    def connectMainSQL(self, path, tableName=None):
        '''make a connection to a database on the disk'''
        if tableName == None:
            if self.mainTableName == None:
                raise AttributeError('Cannot connect to database without a main table specified')
            tableName = self.mainTableName
        else:
            self.mainTableName = tableName
        tmp = spatialite_connect(path)
        cur = tmp.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        result = cur.fetchone()
        if (result is None) or (tableName not in result):
            self.maincon = None
            raise sqlite3.OperationalError('No table {} in {}'.format(tableName, path))
        cur.execute('PRAGMA table_info({})'.format(tableName))
        columns = [i[1] for i in cur.fetchall()]
        for attr in self.attributeNames:
            if attr not in columns:
                self.maincon = None
                raise sqlite3.OperationalError('Attribute {} not in table {} in {}'.format(attr, tableName, path))
        self.maincon = tmp
        
        
    def loadCSV(self, filePath):
        '''take the path of a csv file and import the rows into a sql 
        database'''
        try:
            cur = self.maincon.cursor()
        except AttributeError:
            raise AttributeError('SQL connection not established')
        try:
            #if the file has been loaded, skip
            cur.execute('INSERT INTO metadata (filename) VALUES (?)', (filePath,))
        except sqlite3.IntegrityError:
            return False
        
        with open(filePath, 'rb') as csvfile:
            dr = csv.DictReader(csvfile) # comma is default delimiter
            for i in dr:
                to_db = []
                try:
                    for name in self.attributeNames:
                        to_db.append(i[name])
                except KeyError:
                    return False #tell the calling function that the file cant load
                sqlVals = tuple(to_db)
                sqlStatement = "INSERT INTO CSVdata {} VALUES {};".format(self.attributeNamesTuple, sqlVals)
                cur.execute(sqlStatement)
        self.maincon.commit()
        return True
    
    def writeTableToCSV(self, path, tableName):
        try:
            cur = self.maincon.cursor()
        except AttributeError:
            raise AttributeError('SQL connection not established')
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
        if tableName is None:
            tableName = self.mainTableName
        try:
            cur = self.maincon.cursor()
        except AttributeError:
            raise AttributeError('SQL connection not established')
        if indexName is not None:
            cur.execute('SELECT DISTINCT {} from {} WITH(INDEX({}))'.format(column,tableName, indexName))
        else:
            cur.execute('SELECT DISTINCT {} from {}'.format(column,tableName))
        result = [ str(list(i)[0]) for i in cur.fetchall()]
        return result
        
    def pullXYData(self, keyCol, keyName, xName, yName):
        '''Get data set for specific keyname'''
        data = []
        try:
            cur = self.maincon.cursor()
        except AttributeError:
            raise AttributeError('SQL connection not established')
        cur.execute('SELECT {}, {} FROM CSVdata WHERE {} == "{}"'.format(xName, yName, keyCol, keyName))
        for row in cur:
            if (row[0] == '') or  (row[1] == ''):
                pass
            else:
                x = float(row[0])
                y = float(row[1])
                data.append((x, y))
        return data
        
    def saveMainConToDB(self, path, overwrite=False):
        '''save the main data table 'CSVdata' to SQL db on disk, 
        takes filename'''
        if overwrite:
            try:
                os.remove(path)
            except:
                pass
            #newdb.execute("drop table if exists *")
        newdb = spatialite_connect(path)
        query = "".join(line for line in self.maincon.iterdump())
        newdb.executescript(query)
        newdb.commit()
        return newdb

    def indexTable(self, indexName, tableName, indexCol):
        '''index the main database'''
        try:
            cur = self.maincon.cursor()
        except AttributeError:
            raise AttributeError('SQL connection not established') 
        try:
            cur.execute('CREATE INDEX {} ON {}({})'.format(indexName, tableName, indexCol))
        except sqlite3.OperationalError as e:
            if str(e) == 'index {} already exists'.format(indexName):
                pass
            else:
                raise(sqlite3.OperationalError(str(e)))
        self.maincon.commit()

    def close(self):
        '''close the db connection'''
        self.maincon.close()
        
    def dropTable(self, tableName):
        '''simple table drop'''
        try:
            cur = self.maincon.cursor()
        except AttributeError:
            raise AttributeError('SQL connection not established') 
        cur.execute('DROP TABLE {}'.format(tableName))
        
    def filter(self, srcCol, path, srcTable, maskTable, srcGeoCol, maskGeoCol):
        '''column is the name of the column to return on a match'''
        try:
            cur = self.maincon.cursor()
        except AttributeError:
            raise AttributeError('SQL connection not established') 
        
        sql = "ATTACH DATABASE '{}' AS 'db'".format(path)
        cur.execute(sql)
        
        try:
            cur.execute('SELECT {}.{} FROM db.{}'.format(maskTable, maskGeoCol, maskTable) )
        except sqlite3.OperationalError:
            logging.critical('Failed to attach database "{}": table querry failed'.format(path))
            raise sqlite3.OperationalError('Database {} attach failed'.format(path))
        
        #use spatialindex for querry. diff on gsoy set 100s down to 75s
        sql = "SELECT {} ".format(srcCol)
        sql += "FROM {} AS s, db.{} AS m ".format(srcTable, maskTable)
        sql += "WHERE Within(s.{}, m.{}) = 1 ".format( srcGeoCol, maskGeoCol)
        sql += "AND m.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE " 
        sql += "f_table_name = 'DB=db.{}' AND search_frame = m.{})".format(maskTable, maskGeoCol)
        cur.execute(sql)
        
        result = [ str(list(i)[0]) for i in cur.fetchall()]
        cur.execute('DETACH db')
        self.maincon.commit
        return result
    
    def applyFunction(self, keyCol, keySet, xLable, yLable, outputTable, function):
        '''Get the data for the entries in the teySet list. 
        keyCol is the name for the column that keySet is querried,
        xLable, yLable is the cols to pull data,
        outputTable, outputCol is what sql table and col to park the results
        function is the function to apply to each dataset
        '''
        try:
            cur = self.maincon.cursor()
        except AttributeError:
            raise AttributeError('SQL connection not established') 
        
        #create a column for the result, process the first data entry
        #to get the dictionary keys to put in the table        
        data = self.pullXYData(keyCol, keySet[0], xLable, yLable)
        result = function(data)
        for keyName in result:
            sql = "ALTER TABLE {} ADD {} FLOAT".format(outputTable, keyName)
            cur.execute(sql)
        
        #now pull the data for real
        for key in keySet:
            data = self.pullXYData(keyCol, key, xLable, yLable)
            result = function(data)
            for item in result:
                sql = "UPDATE {} SET {} = {} WHERE {} = '{}'".format(outputTable, item, result[item], keyCol, key)
                cur.execute(sql)    
        self.maincon.commit()
        
        
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
