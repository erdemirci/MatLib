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
import shutil
import sys
from PySide2 import QtWidgets, QtCore, QtUiTools, QtGui

main_path = os.path.dirname(os.path.abspath(__file__))
setup_path = os.path.abspath(os.path.join(main_path, os.pardir))
ui_path = os.path.join(setup_path, 'Ui')
ui_icon_path = os.path.join(ui_path, 'icons')

version = sys.version_info.major

if version == 3:
    long = int
    basestring = str

class TransferWindow(QtWidgets.QMainWindow):
	def __init__(self, parent, config_path, app, renderer, category_folderName):
		super(TransferWindow, self).__init__(parent)
		self.setWindowTitle('MatLib Material Transfer')
		self.setContentsMargins(QtCore.QMargins(0,0,0,0))
		self.setWindowIcon(QtGui.QIcon(os.path.join(ui_icon_path, 'MatlibLogoNS_small.svg')))

		top_Vlayout = QtWidgets.QVBoxLayout()
		scnd_Hlayout = QtWidgets.QHBoxLayout()
		from_layout = QtWidgets.QVBoxLayout()
		catsanshaders_layout = QtWidgets.QHBoxLayout()
		cat_layout = QtWidgets.QVBoxLayout()
		shdr_layout = QtWidgets.QVBoxLayout()
		to_layout = QtWidgets.QVBoxLayout()


		from_label = QtWidgets.QLabel('From:')
		from_layout.addWidget(from_label)
		

		self.from_repository = QtWidgets.QComboBox(self)
		from_layout.addWidget(self.from_repository)


		cat_label = QtWidgets.QLabel('Categories:')
		self.cat_listview = QtWidgets.QListWidget()
		cat_layout.addWidget(cat_label)
		cat_layout.addWidget(self.cat_listview)


		shdr_label = QtWidgets.QLabel('Materials:')
		self.material_listview = QtWidgets.QListWidget()
		self.material_listview.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
		shdr_layout.addWidget(shdr_label)
		shdr_layout.addWidget(self.material_listview)

		icon_size = QtCore.QSize(26,26)

		eq_icon_label = QtWidgets.QLabel('')
		eq_icon = QtGui.QPixmap(os.path.join(ui_icon_path, 'M_toArrow.svg'))
		eq_icon_label.setPixmap(eq_icon.scaled(icon_size))

        
		to_icon_label = QtWidgets.QLabel('')
		to_icon = QtGui.QPixmap(os.path.join(ui_icon_path, 'm_exptoArrow.svg'))
		to_icon_label.setPixmap(to_icon.scaled(icon_size))


		to_label = QtWidgets.QLabel('To:')
		to_layout.addWidget(to_label)
		self.to_repository = QtWidgets.QComboBox(self)
		to_layout.addWidget(self.to_repository)

		to_cat_label = QtWidgets.QLabel('Categories')
		to_layout.addWidget(to_cat_label)
		self.to_cat_listview = QtWidgets.QListWidget()
		to_layout.addWidget(self.to_cat_listview)


		self.export_button = QtWidgets.QPushButton('Export Materials')
		self.export_button.clicked.connect(self.CopyCheck)

		vertSpacer = QtWidgets.QSpacerItem(1, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
		space_layout = QtWidgets.QHBoxLayout()
		space_layout2 = QtWidgets.QHBoxLayout()

		space_layout.addItem(vertSpacer)
		space_layout.addWidget(eq_icon_label)
		space_layout.addItem(vertSpacer)
		
		space_layout2.addItem(vertSpacer)
		space_layout2.addWidget(to_icon_label)
		space_layout2.addItem(vertSpacer)
		
		top_Vlayout.addLayout(scnd_Hlayout)
		scnd_Hlayout.addLayout(from_layout)
		from_layout.addLayout(catsanshaders_layout)
		catsanshaders_layout.addLayout(cat_layout)
		catsanshaders_layout.addLayout(space_layout)

		catsanshaders_layout.addLayout(shdr_layout)
		catsanshaders_layout.addLayout(space_layout2)
		scnd_Hlayout.addLayout(to_layout)
		top_Vlayout.addWidget(self.export_button)

		self.material_listview.setFocusPolicy(QtCore.Qt.NoFocus)
		self.cat_listview.setFocusPolicy(QtCore.Qt.NoFocus)
		self.to_cat_listview.setFocusPolicy(QtCore.Qt.NoFocus)

		self.from_repository.currentIndexChanged.connect(self.ReadCategoriesFromRepository)
		self.to_repository.currentIndexChanged.connect(self.WriteCategoriesFromRepository)

		self.config = config_path
		self.app = app
		self.renderer = renderer
		self.category = category_folderName
		self.mat_dir = None
		self.from_rep_path = None
		self.to_rep_path = None

		self.cat_listview.itemClicked.connect(self.MaterialList)

		transfer_dialog = QtWidgets.QWidget()
		transfer_dialog.setLayout(top_Vlayout)
		self.setCentralWidget(transfer_dialog)


	def ReadCategoriesFromRepository(self):
		try:
			from_repo_select = self.from_repository.currentText()
			self.cat_listview.clear()
			self.material_listview.clear()
			with open(self.config, "r") as f:
				file_data = json.load(f)
			for idx,file in enumerate(file_data[self.app][self.renderer]["repository"]):
				if from_repo_select == file:
					item_index = idx
					break

			root = os.path.join(file_data[self.app][self.renderer]["dirs"][item_index], self.app, self.renderer, self.category)
			self.mat_dir = root
			for dirs in os.listdir(root):
				self.cat_listview.addItem(dirs)
		except:
			pass


	def MaterialList(self, text):
		root = os.path.join(self.mat_dir,text.text())
		self.material_listview.clear()

		for dirs in os.listdir(root):
			self.material_listview.addItem(dirs)


	def WriteCategoriesFromRepository(self):
		try:
			to_repo_select = self.to_repository.currentText()
			self.to_cat_listview.clear()

			with open(self.config, "r") as f:
				file_data = json.load(f)
			for idx,file in enumerate(file_data[self.app][self.renderer]["repository"]):
				if to_repo_select == file:
					item_index = idx
					break

			root = os.path.join(file_data[self.app][self.renderer]["dirs"][item_index], self.app, self.renderer, self.category)
			for dirs in os.listdir(root):
				self.to_cat_listview.addItem(dirs)
		except:
			pass


	def CopyCheck(self):
		try:
			items = self.material_listview.selectedItems()

			from_rep = self.from_repository.currentText()
			from_cat = self.cat_listview.selectedItems()[0].text()
			to_rep = self.to_repository.currentText()
			to_cat = self.to_cat_listview.selectedItems()[0].text()

			self.selected_shaders = []
			for i in items:
				self.selected_shaders.append(i.text())

			if from_cat == to_cat and from_rep == to_rep:
				QtWidgets.QMessageBox.about(self, 'Error', 'Categories are identical.\nIn order to execute this action\nselect a different repository or category.')
			elif len(self.selected_shaders) == 0:
				QtWidgets.QMessageBox.about(self, 'Error', 'Select one or more materials.')
			else:
				with open(self.config, "r") as f:
					file_data = json.load(f)

				for idx,file in enumerate(file_data[self.app][self.renderer]["repository"]):
					if from_rep == file:
						from_idx = idx
					if to_rep == file:
						to_idx = idx

				self.from_rep_path = os.path.join(file_data[self.app][self.renderer]["dirs"][from_idx], self.app, self.renderer, self.category, from_cat)
				self.to_rep_path = os.path.join(file_data[self.app][self.renderer]["dirs"][to_idx], self.app, self.renderer, self.category, to_cat)


				#Check if item exists
				self.matching_names = []
				for i in os.listdir(self.to_rep_path):
					for shader in self.selected_shaders:
						if i == shader:
							self.matching_names.append(i)
						
				self.non_matching_names = list(set(self.selected_shaders)-set(self.matching_names))

				if len(self.matching_names) > 0:
					self.rename_dialog = QtWidgets.QDialog(self)
					rename_layout = QtWidgets.QVBoxLayout()
					self.rename_dialog.setLayout(rename_layout)
					self.rename_dialog.setWindowTitle('Rename Matching Materials')

					for names in self.matching_names:
						self.rename_label = QtWidgets.QLineEdit()
						self.rename_label.setText(names)
						rename_layout.addWidget(self.rename_label)

					self.rename_button = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, self.rename_dialog)
					rename_layout.addWidget(self.rename_button)

					self.rename_button.accepted.connect(self.RenameCheck)
					self.rename_button.rejected.connect(self.rename_dialog.reject)

					self.rename_dialog.show()

				else:
					data = {}
					for i in self.selected_shaders:
						data[i] = i
					self.CopyCategories(data)
		except:
			QtWidgets.QMessageBox.about(self, 'Error', 'Selection is not complete.\nMake sure to select from all 3 lists.')


	def RenameCheck(self):
		renamed_list = []
		re_run = -1
		for widget in self.rename_dialog.children():
			if isinstance(widget, QtWidgets.QLineEdit):
				replaced_name = widget.text()
				for check in renamed_list:
					if check == replaced_name:
						QtWidgets.QMessageBox.about(self, 'Warning', 'There are materials with same name.')
						re_run = 1
						break
				if re_run == -1:
					renamed_list.append(replaced_name)

		collected_materials = []
		for dirs in os.listdir(self.to_rep_path):
			collected_materials.append(dirs)

		#print "widget_list: {}".format(widget_list)
		#print "collet_list: {}".format(collected_materials)

		result = list(set(renamed_list)&set(collected_materials))

		if len(result) > 0:
			QtWidgets.QMessageBox.about(self, 'Warning', '{} is already in the category'.format(', '.join([str(r) for r in result])))

		else:
			data = {}
			for idx,i in enumerate(self.matching_names):
				data[i] = renamed_list[idx]
			for i in self.non_matching_names:
				data[i] = i
			self.CopyCategories(data)
			self.rename_dialog.close()


	def CopyCategories(self, data):
		for keys,vals in data.items():
			source = os.path.join(self.from_rep_path, keys)
			destination = os.path.join(self.to_rep_path, vals)
			shutil.copytree(source, destination)

			json_paths = []
			for root,dirs,files in os.walk(destination):
				for file in files:
					if os.path.basename(root) != "textures" and keys in file:
						extension = os.path.splitext(file)[1]
						path = os.path.join(root, vals + extension)
						if "_icon" in file:
							path = os.path.join(root, vals + '_icon' + extension)

						os.rename(os.path.join(root, file), path)

						if extension == '.json':
							json_paths.append(path)
							
			texture_path = os.path.abspath(os.path.join(os.path.dirname(root), "textures"))
			for path in json_paths:
				with open(path, "r") as f:
					file_data = json.load(f)
					for keys,vals in file_data.items():
						if keys != 'description':
							for k,v in vals["parms"].items():
								if isinstance(v, basestring) and os.path.exists(v):
									file_data[keys]["parms"][k] = os.path.join(texture_path, os.path.basename(v))

				open(path, "w").write(json.dumps(file_data,indent=4))

		QtWidgets.QMessageBox.about(self, 'Transfer Complete', 'Materials are exported.')

			








