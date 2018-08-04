import csv
import numpy
from sets import Set
import os

class DataInterface():
    def __init__(self):
        self.csvFiles = []# list of csv file objects
        self.QGIS = []
        self.Arch = []
        self.categoryLable = None
        self.xLable = None
        self.yLable = None
        self.copyAttributeLables = []

    
    def loadFolder(self, folderPath):
        '''Get a list of csv files in the provided directory and
            add each file with the addCsvFile function'''
        for file in os.listdir(folderPath):
            if file.endswith(".csv"):
                self.addCSVFile(os.path.join(folderPath, file))


    def addCSVFile(self, fileName):
        '''Create a new csv file object and add it to an array '''
        newF = CSVFile(fileName)
        self.csvFiles.append(newF)
        
    def getCSVFileList(self, filterInvalid=True):
        '''Return a list of the files that have been added with
            the option to filter out the files that dont have 
            valid attributes'''
            
        fileList = []
        for f in self.csvFiles:
            if filterInvalid:
                if f.validLables:
                    fileList.append(f.path)
            else:
                fileList.append(f.path)
        return fileList
            
    def setCategoryLable(self, name):
        self.categoryLable = name
        
    def setXLable(self, lable):
        self.xLable = lable
        
    def setYLable(self, lable):
        self.yLable = lable
        
    def addCopyAttributeLable(self, lable):
        if lable not in self.copyAttributeLables:
            self.copyAttributeLables.append(lable)
        

    
    def getCSVNameList(self):
        '''iterat through all the CSV files in the list,
            read every line and record every unique name and return
            a list of them'''
        nameList = {}
        count = 0
        for fileObj in [f for f in self.CSV if f.validLables]:
            count += 1
            fileName = fileObj.name
            nameIndex = fileObj.getIndex(self.name)
            with open(fileName, 'rb') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
                for row in spamreader:
                    nameVal = row[nameIndex]
                    if nameVal == self.name:
                        pass
                    if nameVal not in nameList:
                        nameList[nameVal] = [fileName]
                    else:
                        if fileName not in nameList[nameVal]:
                            nameList[nameVal].append(fileName)
        self.cvsStationIndex = nameList
        return list(nameList)
                    
        #call get csv name date
    def getCSVNameData(self, uniqueName):
        dataPoints = []
        dataObj = DataSeries(uniqueName)
        for fileObj in [fil for fil in self.CSV if fil.name in self.cvsStationIndex[uniqueName]]:
            fileName = fileObj.name
            nameInd = fileObj.getIndex(self.name)
            #print nameInd, uniqueName, fileName
           # print fileObj.indexDict
            
            xInd = fileObj.getIndex(self.xLable)
            yInd =  fileObj.getIndex(self.yLable)
            with open(fileName, 'rb') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
                for row in spamreader:
                    if row[nameInd] == uniqueName:
                        #print uniqueName,row[xInd], row[yInd]
                        dataObj.addDataPoint(row[xInd], row[yInd])
                        for attr in self.copyAttributeLables:
                            if attr not in dataObj.copyAtttributes: #try to avoid direct access
                                try:
                                    dataObj.addCopyAttribute(attr, row[fileObj.getIndex(attr)])
                                except ValueError:
                                    pass
                        
                        #add copy data
        return dataObj

    def getFileCountAll(self):
        c = 0
        for i in self.csvFiles:   
            c += 1
        return c
        
    def getFileCountValid(self):
        c = 0
        for i in self.csvFiles:
            if i.validLables:
                c += 1
        return c
        
    def indexCSVFiles(self):
        '''Takes array of the first line of CSV file and
            locates the indices of the three attribute columns
            we need for analysis'''
        if (self.categoryLable == None) or (self.xLable == None) or (self.yLable == None):
            raise ValueError('cant index files without lables set')
        for fileObj in self.csvFiles:
            fileName = fileObj.path
            with open(str(fileName), 'rb') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
                for row in spamreader:
                    try:
                        fileObj.addIndex(self.categoryLable, row.index(self.categoryLable))
                        fileObj.addIndex(self.xLable, row.index(self.xLable))
                        fileObj.addIndex(self.yLable, row.index(self.yLable))
                        for name in self.copyAttributeLables:
                            if (name in row):
                                fileObj.addIndex(name, row.index(name))
                    except ValueError:
                        fileObj.validLables = False
                    break
class DataSeries():
    def __init__(self, name, xLable = 'x', yLable = 'y'):
        '''init the data object'''
        self.name = name
        self.xLable = xLable
        self.yLable = yLable
        self.copyAtttributes = {}
        self.dataPoints = []
        self.linearRegCoef = [] #[slope, intercept]
        #stats 
        self.zScore = None
        self.risidualSum = None
        
    def addDataPoint(self, xVal, yVal):
        try:
            xVal = float(xVal)
            yVal = float(yVal)
        except Exception:
           # print 'cant make ({}, {}) floats'.format(xVal, yVal)
            return
        self.dataPoints.append((xVal, yVal))
        
    def addCopyAttribute(self, attrLable, attrVal):
        if attrLable not in self.copyAtttributes:
            self.copyAtttributes[attrLable] = attrVal

class CSVFile():
    def __init__(self, path):
        self.path = path
        self.indexDict = {}
        self.validLables = True
    
    def addIndex(self, lable, loc):
        if lable not in self.indexDict:
            self.indexDict[lable] = loc
            
    def getIndex(self, lable):
        if lable in self.indexDict:
            return self.indexDict[lable]
