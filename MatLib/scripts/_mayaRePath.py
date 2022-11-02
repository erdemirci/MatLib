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
#


# Progress bar was added based on Fredrik Averpil's tutorial.
# https://fredrikaverpil.github.io/2015/05/12/file-copy-progress-window-with-pyqt-pyside-and-shutil/

import maya.cmds as cmds
import os
import shutil
import sys
import _color
import re
#reload(_color)
from PySide2 import QtGui, QtCore, QtWidgets

main_path = os.path.dirname(os.path.abspath(__file__))
setup_path = os.path.abspath(os.path.join(main_path, os.pardir))
ui_path = os.path.join(setup_path, 'Ui')
ui_icon_path = os.path.join(ui_path, 'icons')

version = sys.version_info.major

if version == 3:
    long = int
    basestring = str

class MayaRepath(QtWidgets.QMainWindow):
	def __init__(self, parent, reason, items):
		super(MayaRepath, self).__init__(parent)
		
		self.setGeometry(10,100,600,100)
		self.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
		self.setWindowTitle('MatLib Texture Transfer')
		self.setWindowIcon(QtGui.QIcon(os.path.join(ui_icon_path, 'MatlibLogoNS_small.svg')))

		self.reason = reason
		self.sel = items

		layout = QtWidgets.QVBoxLayout()

		self.pb = QtWidgets.QProgressBar()
		self.pb.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
		self.pb.setMaximum(100)
		self.pb.setValue(0)

		self.src_info = QtWidgets.QLabel()
		#self.src_info.setAlignment(QtCore.Qt.AlignCenter)
		self.dst_info = QtWidgets.QLabel()
		#self.dst_info.setAlignment(QtCore.Qt.AlignCenter)

		self.counter = QtWidgets.QLabel()
		self.counter.setAlignment(QtCore.Qt.AlignCenter)

		self.setStyleSheet('''
						QLabel {
							font-size : 12px;
						}
						QProgressBar {
							text-align : center;

						}
						QProgressBar::chunk {
							background-color : %s;

						}
							''' %(_color.__selectedbackground__))
						
						
						

		self.counter.setStyleSheet('''font-size : 18px;

									''')

		layout.addWidget(self.pb)
		layout.addWidget(self.counter)
		layout.addWidget(self.src_info)
		layout.addWidget(self.dst_info)

		self.src = None
		self.dst = None

		progress_widget = QtWidgets.QWidget()
		progress_widget.setLayout(layout)
		self.setCentralWidget(progress_widget)

		data = self.CopyFilesRepath()

		self.auto_start_timer = QtCore.QTimer()
		self.auto_start_timer.timeout.connect( lambda : self.TransferFiles(data, callback_progress=self.progress, callback_copydone=self.complete, chunksize=8192) )
		self.auto_start_timer.start(2000)


	def CopyFilesRepath(self):
		
		connects = []
		collection = {}

		project_folder = cmds.workspace(q=True, rootDirectory = True)
		img_folder = os.path.abspath(os.path.join(project_folder, 'sourceimages', 'MatLib_images'))
		if not os.path.exists(os.path.abspath(os.path.join(project_folder, 'sourceimages'))): 
			os.mkdir(os.path.abspath(os.path.join(project_folder, 'sourceimages')))

		for mat in cmds.listConnections(self.sel):
			if not "defaultShaderList" in mat and not "lightLinker" in mat and not "renderPartition" in mat and not "materialInfo" in mat and not cmds.objectType(mat) == 'transform' and not cmds.objectType(mat) == 'camera' and not "hyperShadePrimaryNodeEditorSavedTabsInfo" in mat and not "MayaNodeEditorSavedTabsInfo" in mat:
				connects.append(mat)

		i = 0
		while i < len(connects):
			items = cmds.listConnections(connects[i], sh=True, s=True, d=False)
			if items == None:
				i += 1
			else:
				for item in items:
					if not "defaultColorMgtGlobals" in item and item not in connects and not cmds.objectType(item) == 'transform' and not "time1" in item and not "expression" in item and not cmds.objectType(item) == 'camera' and not "hyperShadePrimaryNodeEditorSavedTabsInfo" in item and not "MayaNodeEditorSavedTabsInfo" in item:
						connects.append(item)
				i += 1
		
		for connect in connects:
			object_parms = cmds.listAttr(connect, hasData=True, visible=True, multi=True)
			for parm in object_parms:
				try:
					if not '[' in parm:
						value = cmds.getAttr('{}.{}'.format(connect, parm))
						if isinstance(value, basestring):
							path = os.path.abspath(value)
							if os.path.isfile(path):
								org_name = os.path.basename(value)
								new_path = os.path.abspath(os.path.join(img_folder, org_name))
								folder = os.path.abspath(os.path.join(path, os.pardir))
								data_items = []
								if not os.path.exists(img_folder):
								 	os.mkdir(img_folder)
								try:
									extless_name = org_name.replace('.' + org_name.split('.')[-1], '')
									ext = org_name.replace(extless_name, '')
									check_mode = -1
									seq_raw_name = None
									seq_f = None
									seq_check_mode = None
									tiling_mode = cmds.getAttr('{}.{}'.format(connect,'uvTilingMode'))
									sequence_mode = cmds.getAttr('{}.{}'.format(connect,'useFrameExtension'))

									if sequence_mode == 1:
										seq_f = self.tilecheck(org_name, 3)
										seq_check_mode = 3

									if tiling_mode == 1 or tiling_mode == 2:
										f = self.tilecheck(org_name, 1)
										check_mode = 1
									elif tiling_mode == 3 or tiling_mode == 4:
										f = self.tilecheck(org_name, 2)
										check_mode = 2
									
									if tiling_mode > 0 or sequence_mode == 1:
										for cur_file in os.listdir(folder):
											if tiling_mode > 0:
												look_for = cur_file[f.span()[0]: f.span()[-1]]
												compare = self.tilecheck(look_for, check_mode)
												raw_name = re.sub(f.group(), '', org_name)
												if compare and cur_file.endswith(ext):
													compare_raw = re.sub(look_for, '', cur_file)
													if compare_raw == raw_name:
														data_items.append(cur_file)

											if sequence_mode == 1:
												seq_raw_name = re.sub(seq_f.group(), '', org_name)
												look_for = cur_file[seq_f.span()[0]: seq_f.span()[-1]]
												compare = self.tilecheck(look_for, seq_check_mode)
												if compare and cur_file.endswith(ext):
													compare_raw = re.sub(look_for, '', cur_file)
													if compare_raw == seq_raw_name:
														data_items.append(cur_file)

										if len(data_items) == 0:
											data_items.append(org_name)

									else:
										data_items.append(org_name)

								except:
									data_items.append(org_name)


								data = {}
								for i in data_items:
									new_path = os.path.join(img_folder, i)
									old_path = os.path.join(folder, i)
									if new_path != old_path:
										data[i] = {old_path : new_path}
								collection["{}.{}".format(connect, parm)] = data
				except:
					pass

		return collection


	def tilecheck(self, item, mode):
		if mode == 1:
			return re.search(r'u\d_v\d', item)

		elif mode == 2:
			return re.search(r'\d\d\d\d', item)

		elif mode == 3:
			return re.search(r'\d+', item)


	def TransferFiles(self, data, callback_progress, callback_copydone, chunksize):
		items = []
		for k,v in data.items():
			items.append(v.keys())
		
		result = [x for xs in items for x in xs]
		item_count = len(result)
		
		counter = 0
		c = 0
		c_max = 50

		try:
			self.auto_start_timer.stop()
		except:
			print ('Error: could not stop QTimer')

		for key in data.keys():
			color_space = cmds.getAttr('{}.{}'.format(key.split('.')[0], 'colorSpace'))
			for k,v in data[key].items():
				src = list(v.keys())[0]
				dst = list(v.values())[0]
				
				if self.reason == True:
					counter += 1
					if src == dst:
						self.pb.setValue(100)
						self.close()
						continue
					else:
						with open(src, 'rb') as fsrc:
							with open(dst, 'wb') as fdst:
								copied = 0
								while True:
									buf = fsrc.read(chunksize)
									if not buf:
										break
									fdst.write(buf)
									copied += 1
									c += 1
									if c == c_max:
										callback_progress(fsrc=fsrc, fdst=fdst, copied=copied, src=src, dst=dst, max_count=item_count, current_count=counter)
										c = 0
								callback_copydone(max_count=item_count, current_count=counter)

				cmds.setAttr(key, dst, type='string')
				cmds.setAttr('{}.{}'.format(key.split('.')[0], 'colorSpace'), color_space, type='string')

	def progress(self, fsrc, fdst, copied, src, dst, max_count, current_count):
		size_src = os.stat( fsrc.name ).st_size
		size_dst = os.stat( fdst.name ).st_size

		out_src = '<font color = "{}" >Source : </font>'.format(_color.__titlecolor__) + src
		out_dst = '<font color = "{}" >Destination : </font>'.format(_color.__titlecolor__) + dst

		self.src_info.setText(out_src)
		self.dst_info.setText(out_dst)
		self.counter.setText('Copied {} items out of {}.'.format(current_count, max_count))

		float_src = float( size_src )
		float_dst = float( size_dst )

		percentage = int(float_dst/float_src*100)

		try:
			self.pb.setValue( percentage )
		except:
			pass

	def complete(self, max_count, current_count):
		self.pb.setValue(100)
		if current_count == max_count:
			self.close()
			QtWidgets.QMessageBox.about(self, 'Transfer Info', 'Transfer Completed.')
