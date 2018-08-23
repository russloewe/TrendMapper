import csv, sqlite3
import os

class DataInterface():
    
    def __init__(self):
        self.attributeNames = []
        
    def setAttributeNames(self, names):
        '''add attributes to an array that will be copied from 
        the input CSV to the SQL database'''
        for name in names:
            if name not in self.attributeNames:
                self.attributeNames.append(name)
        self.attributeNamesTuple = tuple(self.attributeNames)
    
    def initSQL(self):
        self.con = sqlite3.connect(":memory:")
        self.conout = sqlite3.connect(":memory:")
        self.conmeta = sqlite3.connect(":memory:")
        curR = self.con.cursor()
        cur2 = self.conout.cursor()
        cur3 = self.conmeta.cursor()
        if len(self.attributeNames) < 1:
            raise AttributeError("no attributes specified, cant init SQL")
        curR.execute("CREATE TABLE CSVdata (ID int PRIMARY KEY)")
        cur2.execute("CREATE TABLE resultdata (ID int)")
        cur3.execute("CREATE TABLE metadata (filename VARCHAR(200) UNIQUE)")
        for name in self.attributeNames:
            curR.execute("ALTER TABLE CSVdata ADD {} VARCHAR(50)".format(name))
            cur2.execute("ALTER TABLE resultdata ADD {} VARCHAR(50)".format(name))
        self.con.commit()
        self.conout.commit()
        self.conmeta.commit()
   
    def close(self):
        '''close the sql connection'''
        self.con.close()
        self.con = None
    
    def connectSQL(self, path):
        self.con = sqlite3.connect(path)
    
    def loadCSV(self, filePath):
        '''take the path of a csv file and import the rows into a sql 
        database'''
        try:
            cur = self.con.cursor()
            curmeta = self.conmeta.cursor()
        except AttributeError:
            raise AttributeError('SQL connection not established')
        try:
            #if the file has been loaded, skip
            curmeta.execute('INSERT INTO metadata (filename) VALUES (?)', (filePath,))
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
        self.con.commit()
        return True
    
    def writeResultsToCSV(self, path):
         with open(path, 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
            #write header to first line, self.unk is original unique key
            header = [f for f in self.dataSets[0].dataStats]          
            spamwriter.writerow(header) 
            for data in self.dataSets:
                row = [data.dataStats[key] for key in header]
                spamwriter.writerow(row) 
    
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
            cur = self.con.cursor()
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
            cur = self.con.cursor()
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
        query = "".join(line for line in self.con.iterdump())
        newdb.executescript(query)
        
    def saveResultsToDB(self, path, overwrite=False):
        '''save the main data table 'CSVdata' to SQL db on disk, 
        takes filename'''
        
        newdb = sqlite3.connect(path)
        if overwrite:
            newdb.execute("drop table if exists resultdata")
        query = "".join(line for line in self.conout.iterdump())
        newdb.executescript(query)

           
