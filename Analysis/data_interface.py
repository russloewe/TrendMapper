import csv, sqlite3
import os

class DataInterface():
    
    def __init__(self):
        self.attributeNames = []
    
    def test(self):
        pass
        
    def setAttributeNames(self, names):
        '''add attributes to an array that will be copied from 
        the input CSV to the SQL database'''
        for name in names:
            if name not in self.attributeNames:
                self.attributeNames.append(name)
        self.attributeNamesTuple = tuple(self.attributeNames)
    
    def initSQL(self):
        self.con = sqlite3.connect(":memory:")
        self.con.enable_load_extension(True)
        curR = self.con.cursor()
        if len(self.attributeNames) < 1:
            raise AttributeError("no attributes specified, cant init SQL")
        curR.execute("CREATE TABLE CSVdata (dummy int)")
        for name in self.attributeNames:
            curR.execute("ALTER TABLE CSVdata ADD {} VARCHAR(50)".format(name))
        self.con.commit()

    def loadCSV(self, filePath):
        '''take the path of a csv file and import the rows into a sql 
        database'''
        try:
            cur = self.con.cursor()
        except AttributeError:
            raise AttributeError('SQL connection not established')
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
    
    def writeDataOut(self, path):
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
            keyList.append(row)
        return keyList
        
