from qgis.core import QgsMessageLog

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
        if self.level <= 1:
            QgsMessageLog.logMessage(message, 'TrendMapper', 
                                            level=QgsMessageLog.INFO)
    
    def debug(self, message):
        if self.level == 0:
            QgsMessageLog.logMessage(message, 'TrendMapper',
                                            level=QgsMessageLog.INFO)
    
    def error(self, message):
        if self.level <= 2:
            QgsMessageLog.logMessage(message, 'TrendMapper',
                                        level=QgsMessageLog.CRITICAL)
        
    def critical(self, message):
        if self.level <= 3:
            QgsMessageLog.logMessage(message, 'TrendMapper', 
                                        level=QgsMessageLog.CRITICAL)
        
    def warning(self, message):
        if self.level <= 2:
            QgsMessageLog.logMessage(message, 'TrendMapper', 
                                         level=QgsMessageLog.WARNING)
