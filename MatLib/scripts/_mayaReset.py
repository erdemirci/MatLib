# -*- coding: utf-8 -*-
#
# MatLib - Material Library
#
# Copyright (C) 2022  Erdem Demirci
#
# www.erdemirci3d.com
# erdemirci3d@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import json
import sys
from PySide2 import QtWidgets, QtCore, QtGui
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

version = sys.version_info.major

if version == 3:
	long = int
	basestring = str

def maya_main_window():
	main_window_ptr = omui.MQtUtil.mainWindow()
	return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class ResetWindow(QtWidgets.QMainWindow):
	def __init__(self, parent=maya_main_window()):
		super(ResetWindow, self).__init__(parent)

		appdata_path = os.path.join(os.path.expandvars(r'%LOCALAPPDATA%'),'MatLib')
		self.config_path = os.path.join(appdata_path, 'config.json')
		main_path = os.path.dirname(os.path.abspath(__file__))
		setup_path = os.path.abspath(os.path.join(main_path, os.pardir))
		ui_path = os.path.join(setup_path, 'Ui')
		ui_icon_path = os.path.join(ui_path, 'icons')

		self.app = "Maya"
		self.supported_renderers = ["Redshift", "Arnold", "Vray"]

		self.setContentsMargins(QtCore.QMargins(0,0,0,0))
		self.setWindowTitle('Reset Paths')
		self.setWindowIcon(QtGui.QIcon(os.path.join(ui_icon_path, 'MatlibLogoNS_small.svg')))

		layout = QtWidgets.QVBoxLayout()
		main = QtWidgets.QDialog()

		warning_text = 'This action will remove all the path links from MatLib.It will not delete any of the files or folders.\n Are you sure?'
		warning_label = QtWidgets.QLabel()
		warning_label.setText(warning_text)

		buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel, main)

		layout.addWidget(warning_label)
		layout.addWidget(buttons)

		main.setLayout(layout)
		self.setCentralWidget(main)

		buttons.accepted.connect(self.resetConfig)
		buttons.rejected.connect(self.rejection)



	def resetConfig(self):
		with open(self.config_path, "r") as f:
			file_data = json.load(f)
			for r in self.supported_renderers:
				file_data[self.app][r]['dirs'] = []
				file_data[self.app][r]['current_index'] = 0
				file_data[self.app][r]['repository'] = []

		open(self.config_path, "w").write(json.dumps(file_data, indent=4))
		self.close()

	def rejection(self):
		self.close()
