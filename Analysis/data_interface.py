import csv, sqlite3
import os

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
    
    def initSQL(self, spatialite=True):
        '''set up our initial tmp sql database in memory and init some tables
        maintable: the name to load the incomming dataset, ie, the csv 
        outtable:   the name for the table where well put the results of the analysis
        meta table: name of files that have been loaded to prevent loading a file twice'''
        if len(self.attributeNames) < 1:
            raise AttributeError("no attributes specified, cant init SQL")
        
        self.mainTableName = 'CSVdata'
        self.outTableName = 'resultdata'
        self.maincon = spatialite_connect(":memory:")
        cur = self.maincon.cursor()
        
        if spatialite:
            cur.execute('SELECT InitSpatialMetadata()')
            
        cur.execute("CREATE TABLE {} (ID int PRIMARY KEY)".format(self.mainTableName) )
        cur.execute("CREATE TABLE {} (ID int)".format(self.outTableName) )
        cur.execute("CREATE TABLE metadata (filename VARCHAR(200) UNIQUE)")
        for name in self.attributeNames:
            cur.execute("ALTER TABLE CSVdata ADD {} VARCHAR(50)".format(name))
            cur.execute("ALTER TABLE resultdata ADD {} VARCHAR(50)".format(name))
        self.maincon.commit()
   
    def createGeomIndex(self, indexName, uniqueKey, xName, yName):
        '''create a new table with a geometry point layer for 
        querrying by location'''
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
        try:
            sql = "SELECT AddGeometryColumn('{}', 'geom', 4326, 'POINT', 'XY');".format(indexName)
            cur.execute(sql)
        except:
            cur.execute('SELECT InitSpatialMetadata()')
            sql = "SELECT AddGeometryColumn('{}', 'geom', 4326, 'POINT', 'XY');".format(indexName)
            cur.execute(sql)

        keyList = self.pullUniqueKeys(uniqueKey)
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
            x = str(row[0])
            y = str(row[1])
            data.append((x, y))
        return data
    
    def loadDBToMemory(self, path):
        '''copy a db from the disk to memory and replace the 
        connection'''
        self.connectMainSQL(path)
        self.maincon = self.saveMainConToDB(':memory:')
        
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
        return newdb
        
    def saveTableToDB(self, tableName, path, overwrite=False):
        '''save the main data table 'CSVdata' to SQL db on disk, 
        takes filename'''
        
        newdb = sqlite3.connect(path)
        if overwrite:
            newdb.execute("drop table if exists {}".format(tableName))
        query = "".join(line for line in self.mainconout.iterdump())
        newdb.executescript(query)

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

    def filter(self, column, path, table1, table2, geom1, geom2):
        try:
            cur = self.maincon.cursor()
        except AttributeError:
            raise AttributeError('SQL connection not established') 
        
        sql = "ATTACH DATABASE '{}' AS 'db'".format(path)
        cur.execute(sql)
        
        try:
            cur.execute('SELECT {}.{} FROM db.{}'.format(table2, geom2, table2) )
        except sqlite3.OperationalError:
            raise sqlite3.OperationalError('Database {} attach failed'.format(path))
            
        sql = "SELECT {}.{} FROM {}, {} WHERE Within({}.{}, {}.{})".format(table1, column, table1, table2, table1, geom1, table2, geom2)
        cur.execute(sql)
        result = [ str(list(i)[0]) for i in cur.fetchall()]
        cur.execute('DETACH db')
        self.maincon.commit
        return result
    
        
        
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
