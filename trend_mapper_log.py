from qgis.core import QgsMessageLog

class TrendMapperLogger():
    
    def info(self, message):
        QgsMessageLog.logMessage("Info: {}".format(message),
                                 "TrendMapper", 0)
        
    def warn(self, message):
        QgsMessageLog.logMessage("Warning: {}".format(message),
                                "TrendMapper", 1)
        
    def error(self, message):
        QgsMessageLog.logMessage("Error: {}".format(message),
                                 "TrendMapper", 2)
