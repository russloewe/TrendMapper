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
    
    def initSQL(self):
        self.mainTableName = 'CSVdata'
        self.outTableName = 'resultdata'
        self.maincon = sqlite3.connect(":memory:")
        cur = self.maincon.cursor()
        if len(self.attributeNames) < 1:
            raise AttributeError("no attributes specified, cant init SQL")
        cur.execute("CREATE TABLE {} (ID int PRIMARY KEY)".format(self.mainTableName) )
        cur.execute("CREATE TABLE {} (ID int)".format(self.outTableName) )
        cur.execute("CREATE TABLE metadata (filename VARCHAR(200) UNIQUE)")
        for name in self.attributeNames:
            cur.execute("ALTER TABLE CSVdata ADD {} VARCHAR(50)".format(name))
            cur.execute("ALTER TABLE resultdata ADD {} VARCHAR(50)".format(name))
        self.maincon.commit()
   
    def close(self):
        '''close the sql connection'''
        self.maincon.close()
        self.maincon = None
    
    def connectMainSQL(self, path, tableName=None):
        if tableName == None:
            tableName = self.mainTableName
        tmp = sqlite3.connect(path)
        cur = tmp.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        result = cur.fetchone()
        if (result is None) or (self.mainTableName not in result):
            self.maincon = None
            raise sqlite3.OperationalError('No table {} in {}'.format(tableName, path))
        cur.execute('PRAGMA table_info({})'.format(tableName))
        columns = [i[1] for i in cur.fetchall()]
        print columns
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
            
    def pullUniqueKeys(self, column):
        ''' grab a list of all the unique names in the given
        column'''
        keyList = []
        try:
            cur = self.maincon.cursor()
        except AttributeError:
            raise AttributeError('SQL connection not established')
        cur.execute('SELECT DISTINCT {} from CSVdata'.format(column))
        for row in cur:
            keyList.append(str(row[0]))
        return keyList
        
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

    def saveMainToDB(self, path, overwrite=False):
        '''save the main data table 'CSVdata' to SQL db on disk, 
        takes filename'''
        
        newdb = sqlite3.connect(path)
        if overwrite:
            newdb.execute("drop table if exists CSVdata")
        query = "".join(line for line in self.maincon.iterdump())
        newdb.executescript(query)
        
    def saveResultsToDB(self, path, overwrite=False):
        '''save the main data table 'CSVdata' to SQL db on disk, 
        takes filename'''
        
        newdb = sqlite3.connect(path)
        if overwrite:
            newdb.execute("drop table if exists resultdata")
        query = "".join(line for line in self.mainconout.iterdump())
        newdb.executescript(query)

    def indexMainDb(self):
        '''index the main database'''
        pass       
