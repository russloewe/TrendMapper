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

import os 
from PyQt4 import QtGui, uic, QtCore

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'trend_mapper_status.ui'))


class TrendMapperStatus(QtGui.QDialog, FORM_CLASS):
    def __init__(self, abortCallBack, parent=None):
        """Constructor."""
        super(TrendMapperStatus, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.abortButton.clicked.connect(abortCallBack)
    
    def setProgressBar(self, main, text, maxVal=100):
        self.prgBar.setValue(0)
        self.prgBar.setMaximum(maxVal)

    def ProgressBar(self, value):
        self.prgBar.setValue(value)
        if (value == self.prgBar.maximum()):
            pass
            #self.iface.messageBar().clearWidgets()
            #self.iface.mapCanvas().refresh()