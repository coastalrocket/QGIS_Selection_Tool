# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SelectionTool
                                 A QGIS plugin
 This plugin makes selections easy
                              -------------------
        begin                : 2017-02-02
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Andrew Bailey
        email                : andrewbailey@astuntechnology.com
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
from PyQt4.QtCore import QObject, SIGNAL, Qt, QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon

#from qgis.core import QgsMessageLog, QgsMapLayer
from qgis.core import *
from qgis.gui import *

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from selection_tool_dialog import SelectionToolDialog
import os.path


class SelectionTool:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SelectionTool_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = SelectionToolDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Selection Tool')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SelectionTool')
        self.toolbar.setObjectName(u'SelectionTool')

        #self.dlg.cbxLayer.activated.connect(self.populate_cbxAttributes)
        #self.dlg.btnSelect.clicked.connect(self.hit_select)

        #QgsMessageLog.logMessage("init")
        #print "init"

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SelectionTool', message)

    def printMsg(self, msg):
        #QMessageBox.information(self.iface.mainWindow(), "Debug", msg)
        QgsMessageLog.logMessage(msg)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = SelectionToolDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/SelectionTool/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Selection Tool'),
            callback=self.run,
            parent=self.iface.mainWindow())
        self.dlg.btnSelect.clicked.connect(self.hit_select)
        self.dlg.cbxLayer.activated.connect(self.populate_cbxAttributes)
        self.dlg.cbxAttributes.activated.connect(self.populate_cbxOperator)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Selection Tool'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def populate_cbxLayer(self):
        #QgsMessageLog.logMessage("populate_cbxLayer")
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
            layerType = layer.type()
            if layerType == QgsMapLayer.VectorLayer:
                layer_list.append(layer.name())
        self.dlg.cbxLayer.clear()
        self.dlg.cbxLayer.addItems(layer_list)

    def populate_cbxAttributes(self):
        #QgsMessageLog.logMessage("populate_cbxAttributes")
        """Populates the cbxAttributes with attributes of the selected layer"""
        selectedLayerIndex = self.dlg.cbxLayer.currentIndex()
        selectedLayerName = self.dlg.cbxLayer.currentText()
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
             if layer.name() == selectedLayerName:
                 selectedLayer = layer
                 attribute_index = selectedLayer.attributeList()
                 attribute_list = []
                 for attribute in attribute_index:
                     attribute_list.append(layer.attributeDisplayName(attribute))
                 self.dlg.cbxAttributes.clear()
                 self.dlg.cbxAttributes.addItems(attribute_list)

    def populate_cbxOperator(self):
        #QgsMessageLog.logMessage("populate_cbxOperator")
        selectedLayerName = self.dlg.cbxLayer.currentText()
        selectedAttributeName = self.dlg.cbxAttributes.currentText()
        layers = self.iface.legendInterface().layers()
        for layer in layers:
            if layer.name() == selectedLayerName:
                fields = layer.pendingFields()
                for i in range(fields.count()):
                    field = fields[i]
                    if field.name() == selectedAttributeName:
                        if field.typeName() == "String":
                            self.dlg.cbxOperator.clear()
                            operator_list = ['=', 'LIKE', 'ILIKE']
                            self.dlg.cbxOperator.addItems(operator_list)
                        elif (field.typeName() == "Real") or (field.typeName() == "Integer") or (field.typeName() == "Integer64"):
                            self.dlg.cbxOperator.clear()
                            operator_list = ['=', '>', '<']
                            self.dlg.cbxOperator.addItems(operator_list)
                        elif (field.typeName() == "Date"):
                            self.dlg.cbxOperator.clear()
                            operator_list = ['=', '>', '<']
                            self.dlg.cbxOperator.addItems(operator_list)
                        else:
                            QgsMessageLog.logMessage("Sorry, field type not recognised.")


    def hit_select(self):
        selectedLayerName = self.dlg.cbxLayer.currentText()
        selectedAttributeName = self.dlg.cbxAttributes.currentText()
        selectedOperator = self.dlg.cbxOperator.currentText()
        selectedValue = self.dlg.txtInput.text()
        layers = self.iface.legendInterface().layers()
        for layer in layers:
            if layer.name() == selectedLayerName:
                # type of field
                fields = layer.pendingFields()
                for i in range(fields.count()):
                    field = fields[i]
                    if field.name() == selectedAttributeName:
                        if (field.typeName() == "String") or (field.typeName() == "Date"):
                            treatedValue = '\'' + selectedValue + '\''
                            QgsMessageLog.logMessage(treatedValue)
                            if (field.typeName() == "Date"):
                                QgsMessageLog.logMessage("selection by date is not supported for some sources e.g. Shapefile")
                        else:
                            treatedValue = selectedValue
                # make layer active
                self.iface.legendInterface().setCurrentLayer(layer)
                self.iface.setActiveLayer(layer)
                # make a selection
                exprString = '\"' + selectedAttributeName + '\" ' + selectedOperator + ' ' + treatedValue
                QgsMessageLog.logMessage("expression used: %s" % exprString)
                expr = QgsExpression(exprString)
                it = layer.getFeatures(QgsFeatureRequest(expr))
                ids = [i.id() for i in it]
                layer.setSelectedFeatures(ids)
                QgsMessageLog.logMessage("selected: %s" % str(len(ids)))

    def run(self):
        self.populate_cbxLayer()
        # check for active layer
        active_layer = self.iface.activeLayer()
        if active_layer is not None:
            for i in range(self.dlg.cbxLayer.count()):
                if self.dlg.cbxLayer.itemText(i) == active_layer.name():
                    self.dlg.cbxLayer.setCurrentIndex(i)
                    self.populate_cbxAttributes()
                    self.populate_cbxOperator()
        else:
            self.populate_cbxAttributes()
        self.dlg.txtInput.clear()
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            #pass
            QgsMessageLog.logMessage("ok")
            #print "pass"

# test fails with date equals and less than
# include intrinsic fields