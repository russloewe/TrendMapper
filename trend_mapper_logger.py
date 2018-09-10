from qgis.core import QgsMessageLog
from inspect import currentframe, getframeinfo, stack


class myLogger():
    DEBUG = 0 
    INFO = 1
    ERROR = 2
    CRITICAL = 3
    
    def __init__(self, level=1):
        self.level = level
        
    def setLevel(self, level):
        self.level = level
    
    def info(self, message):
        QgsMessageLog.logMessage(message, 'TrendMapper', level=QgsMessageLog.INFO)
    
    def debug(self, message):
        frameinfo = getframeinfo(currentframe())
        fname = frameinfo.filename.split('/')[-1]
        lineno = frameinfo.lineno
        funame = stack()[0][3]
        QgsMessageLog.logMessage("{}:{}({}): ".format(fname, funame,
                                    lineno), 'TrendMapper',
                                    level=QgsMessageLog.INFO)
        QgsMessageLog.logMessage(message, 'TrendMapper',
                                             level=QgsMessageLog.INFO)
    
    def error(self, message):
        QgsMessageLog.logMessage(message, 'TrendMapper', level=QgsMessageLog.CRITICAL)
        
    def critical(self, message):
        QgsMessageLog.logMessage(message, 'TrendMapper', level=QgsMessageLog.CRITICAL)
