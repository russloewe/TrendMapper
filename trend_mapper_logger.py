# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TrendMapperDialog
                                 A QGIS plugin
 calculate trendlines along catagories
                             -------------------
        begin                : 2018-07-28
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Russell Loewe
        email                : russloewe@gmai.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.core import QgsMessageLog

class TrendMapperLogger():
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
