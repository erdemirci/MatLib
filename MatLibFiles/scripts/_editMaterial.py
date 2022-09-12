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

import json
import os
from PySide2 import QtWidgets, QtCore, QtUiTools, QtGui


class MaterialDisplay(QtWidgets.QMainWindow):
	def __init__(self, parent, renderer):
		super(MaterialDisplay, self).__init__(parent)
		self.setWindowTitle("Material Display Editor")
		self.setContentsMargins(QtCore.QMargins(0,0,0,0))
		self.file_name = None

		if renderer == 'Arnold':
			self.file_name = 'mtoa_Parms.json'
		elif renderer == 'Redshift':
			self.file_name = 'RS_Parms.json'
		elif renderer == 'Vray':
			self.file_name = 'vray_Parms.json'

		#main_path = os.path.dirname(os.path.abspath(__file__))
		#file_path = os.path.join(os.path.abspath(os.path.join(main_path, os.pardir)), 'files')
		appdata_path = os.path.join(os.path.expandvars(r'%LOCALAPPDATA%'),'MatLib')
		self.m_path = os.path.join(appdata_path, self.file_name)
		
		self.data = {}
		self.index = None
		layout = QtWidgets.QVBoxLayout()

		self.pageCombo = QtWidgets.QComboBox()
		self.scrll_area = QtWidgets.QScrollArea()
		self.scrll_area.setFocusPolicy(QtCore.Qt.NoFocus)
		self.scrll_area.setWidgetResizable(True)

		with open(self.m_path, 'r') as f:
			self.data = json.load(f)

		self.pageCombo.addItems(self.data.keys())
		self.pageCombo.activated.connect(self.switchPage)

		cont_widget = QtWidgets.QWidget()
		self.stackedLayout = QtWidgets.QVBoxLayout(cont_widget)
		

		self.button = QtWidgets.QPushButton("Save Changes")
		self.button.clicked.connect(self.buttonExc)

		self.switchPage()

		layout.addWidget(self.pageCombo)

		#cont_widget.setLayout(self.stackedLayout)
		self.scrll_area.setWidget(cont_widget)
		layout.addWidget(self.scrll_area)

		layout.addWidget(self.button)

		mat_display = QtWidgets.QWidget()
		mat_display.setLayout(layout)
		self.setCentralWidget(mat_display)


	def switchPage(self):
		#delete widgets
		while self.stackedLayout.count():
			child = self.stackedLayout.takeAt(0)
			if child.widget():
				child.widget().deleteLater()

		self.index = self.pageCombo.currentText()


		for i in self.data[self.index].keys():
			check = QtWidgets.QCheckBox(self.data[self.index][i]['name'])
			val = self.data[self.index][i]['value']

			if val == 0:
				check.setChecked(False)
			else:
				check.setChecked(True)
			
			
			self.stackedLayout.addWidget(check)


	def buttonExc(self):
		self.index = self.pageCombo.currentText()
		checked_list = []

		for i in range(self.stackedLayout.count()):
			chBox = self.stackedLayout.itemAt(i).widget()
			if chBox.isChecked():
				checked_list.append(chBox.text())

		#print checked_list

		for i in self.data[self.index].keys():
			if self.data[self.index][i]['name'] in checked_list:
				self.data[self.index][i]['value'] = 1
			else:
				self.data[self.index][i]['value'] = 0

		open(self.m_path, "w").write(json.dumps(self.data, indent=4))
