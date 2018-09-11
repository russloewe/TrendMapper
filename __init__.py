# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TrendMapper
                                 A QGIS plugin
 calculate trendlines along catagories
                             -------------------
        begin                : 2018-07-28
        copyright            : (C) 2018 by Russell Loewe
        email                : russloewe@gmai.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load TrendMapper class from file TrendMapper.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .trend_mapper import TrendMapper
    return TrendMapper(iface)
