# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SelectionTool
                                 A QGIS plugin
 This plugin makes selections easy
                             -------------------
        begin                : 2017-02-02
        copyright            : (C) 2017 by Andrew Bailey
        email                : andy@planetnomad.com
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
    """Load SelectionTool class from file SelectionTool.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .selection_tool import SelectionTool
    return SelectionTool(iface)
