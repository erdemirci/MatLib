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

import maya.cmds as cmds
import os
import sys
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtWidgets, QtGui, QtCore
import _mayaRePath
#reload(_mayaRePath)
from _mayaRePath import MayaRepath

main_path = os.path.dirname(os.path.abspath(__file__))
setup_path = os.path.abspath(os.path.join(main_path, os.pardir))
ui_path = os.path.join(setup_path, 'Ui')
ui_icon_path = os.path.join(ui_path, 'icons')

version = sys.version_info.major

if version == 3:
    long = int
    basestring = str

def maya_main_window():
	main_window_ptr = omui.MQtUtil.mainWindow()
	return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class TextureTransferWindow(QtWidgets.QMainWindow):
	def __init__(self, callback=None, parent=maya_main_window()):
		super(TextureTransferWindow, self).__init__(parent)
		
		self.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
		self.setWindowTitle('MatLib Transfer to Project')
		self.setWindowIcon(QtGui.QIcon(os.path.join(ui_icon_path, 'MatlibLogoNS_small.svg')))

		layout = QtWidgets.QVBoxLayout()
		radial_layout = QtWidgets.QHBoxLayout()

		self.rad_button1 = QtWidgets.QRadioButton('Repath nodes and Copy Files')
		self.rad_button1.setChecked(True)
		self.rad_button2 = QtWidgets.QRadioButton('Repath nodes only')

		g_text = '''
This tool will automaticly repath and copy \n
all of the textures to the current Project.

		'''

		grpBox = QtWidgets.QGroupBox('Info')
		grp_layout = QtWidgets.QHBoxLayout()
		info_text = QtWidgets.QLabel()
		info_text.setText(g_text)
		grp_layout.addWidget(info_text)
		grpBox.setLayout(grp_layout)
		

		radial_layout.addWidget(self.rad_button1)
		radial_layout.addWidget(self.rad_button2)

		run = QtWidgets.QPushButton('Execute')

		layout.addLayout(radial_layout)
		layout.addWidget(grpBox)
		layout.addWidget(run)

		run.clicked.connect(self.buttonstate)

		main_wid = QtWidgets.QWidget()
		main_wid.setLayout(layout)

		self.setCentralWidget(main_wid)


	def buttonstate(self):
		sel_error = False
		sel = cmds.selectedNodes()
		if sel == None:
			sel_error = True
			QtWidgets.QMessageBox.about(self, 'Error', 'Select only ShadingGroup(SG) nodes.')

		else:
			for item in sel:
				if not cmds.objectType(item) == 'shadingEngine':
					sel_error = True
					break

			if sel_error == False:
				if self.rad_button1.isChecked() == True:
					load = MayaRepath(self, reason=True, items=sel)
					load.show()
				else:
					self.reason = False
					MayaRepath(self, reason=False, items=sel)

			else:
				QtWidgets.QMessageBox.about(self, 'Error', 'Select ShadingGroup nodes.')


