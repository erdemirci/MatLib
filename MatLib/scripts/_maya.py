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
import maya.app.renderSetup.model.renderSetup as renderSetup
import maya.app.renderSetup.model.renderLayer as renderLayer
import maya.app.renderSetup.model.override as override
import maya.OpenMaya as om
from maya.app.renderSetup.model.connectionOverride import ShaderOverride
import time
import json
import os
import shutil
import sys
from collections import OrderedDict


main_path = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.join(main_path, os.pardir))

version = sys.version_info.major

if version == 3:
    long = int
    basestring = str


file_formats = [".jpg",".jpeg", ".png", ".tiff", ".tif", ".exr", "hdr", ".tga", ".tx", "bmp", ".sgi", ".pic", ".psd", ".tex"]


class SaveFiles():
	def __init__(self, renderer, selection, text, description, item, path, material_folderName, texture_folderName, displayImg_folderName, image_extension, material_extension, texture_icon):
		self.item_name = text
		self.description = description
		self.json_dir = os.path.join(path, item)
		self.ls = cmds.selectedNodes()[0]
		self.description = description
		self.items = {}
		self.mini_items = {}
		self.image_resolution = 800
		self.textureIcon_folderName = texture_icon
		self.material_folderName = material_folderName
		self.texture_folderName = texture_folderName
		self.displayImg_folderName = displayImg_folderName
		self.image_extension = image_extension
		self.material_extension = material_extension
		self.renderer = renderer
		a_string = self.AttributeString()



		self.MaterialCollect(a_string=a_string)
		self.SaveAsJson()
		self.SaveRenderView()


	def AttributeString(self):
		list_val = []
		if self.renderer == 'Redshift':
			list_val = ['rsMaterialId']
		elif self.renderer == 'Arnold':
			list_val = ['aiOverride']
		elif self.renderer == 'Vray':
			list_val = []

		return list_val

	def MaterialCollect(self, a_string):
		connects = []

		#Redshift Material(SG) Inputs
		renderer_parms = {}
		renderer_inputs = {}
		input_items = []
		renderer_items = []
		input_item = None
		output_item = None


		#Render Material Parameters and Inputs (SG)
		for main in cmds.listConnections(self.ls, sh=True, s=True, d=False, c=True, p=True):
			if cmds.objectType(main) != "mesh" and ".dagSetMembers" not in main and ".instObjGroups" not in main:
				input_items.append(main)
		

		for x in range(0,len(input_items),2):
			input_item = input_items[x]
			output_item = input_items[x+1]

			renderer_inputs = {input_item : output_item}
			renderer_items.append(renderer_inputs)

		object_parms = cmds.listAttr(self.ls, hasData=True, keyable=False, visible=True, settable=True, st=a_string)

		value = cmds.getAttr('{}.{}'.format(self.ls, object_parms[0]))
		renderer_parms[object_parms[0]] = value

		self.items[self.ls] = {	
								"name" : cmds.objectType(self.ls),
								"connection" : renderer_items,
								"parms" : renderer_parms
								}

		for mat in cmds.listConnections(self.ls):
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

		collect_texture_files = []
		for connect in connects:
			object_name = cmds.objectType(connect)
			object_input_label = connect
			object_parms = []
			object_parm = {}
			input_item = None
			output_item = None
			connections = []

			items = cmds.listConnections(connect, d=False, s=True, p=True, sh=False, c=True)
			try:
				for x in range(0,len(items),2):
					input_item = items[x]
					output_item = items[x+1]

					if '.linkedCamera' in input_item and '.message' in output_item:
						output_item = 'perspShape.message'

					object_connections = { input_item : output_item}
					connections.append(object_connections)

			except:
				pass


			object_parms = cmds.listAttr(connect, hasData=True, visible=True, multi=True)

			for parm in object_parms:
				try:
					value = cmds.getAttr('{}.{}'.format(connect,parm))
					#print "{} {} {}".format(connect, parm, value)
					object_parm[parm] = value
					if parm == "space_type" and value == 0: #Height Field
						object_parm[parm] = 1

					if isinstance(value, basestring):
						parm_result = os.path.normpath(value)
						if os.path.isfile(parm_result):
							copy = os.path.basename(parm_result)
							object_parm[parm] = os.path.join(self.json_dir, self.item_name, self.texture_folderName, copy)
							if not os.path.exists(os.path.join(self.json_dir,self.item_name, self.texture_folderName)):
								os.makedirs(os.path.join(self.json_dir, self.item_name, self.texture_folderName))
								os.makedirs(os.path.join(self.json_dir, self.item_name, self.textureIcon_folderName))
							

							file_name = os.path.basename(parm_result)

							#Icon Generator
							destination_path = os.path.join(self.json_dir, self.item_name, self.textureIcon_folderName, copy)
							self.IconGenerate(parm_result, destination_path)


							#UDIM and Sequence check
							try:
								tiling_mode = cmds.getAttr('{}.{}'.format(connect,'uvTilingMode'))
								sequence_mode = cmds.getAttr('{}.{}'.format(connect,'useFrameExtension'))

								if any(i.isdigit() for i in file_name) and tiling_mode > 0 or sequence_mode == 1:
									#raw_name = ''.join([i for i in file_name if not i.isdigit()])
									#raw_name = raw_name.split('.')[0]
									extless_name = file_name.replace('.' + file_name.split('.')[-1], '')
									seq_string = ''
									for i in reversed(extless_name):
										if i.isdigit():
											seq_string += i
										else:	
											break
									raw_name = extless_name.replace(seq_string[::-1], '')
									for seq in os.listdir(os.path.dirname(parm_result)):
										if raw_name in seq and seq.endswith('.' + file_name.split('.')[-1]):
											collect_texture_files.append(seq)
											if os.path.dirname(parm_result) != os.path.join(self.json_dir, self.item_name, self.texture_folderName):
												sequence_path = os.path.join(os.path.dirname(parm_result), seq)
												shutil.copy(sequence_path, os.path.join(self.json_dir, self.item_name, self.texture_folderName))

								else:
									collect_texture_files.append(copy)
									#copy files if not self
									if os.path.dirname(parm_result) != os.path.join(self.json_dir, self.item_name, self.texture_folderName):
										shutil.copy(parm_result,os.path.join(self.json_dir, self.item_name, self.texture_folderName, copy))
							except ValueError:
								collect_texture_files.append(copy)
								if os.path.dirname(parm_result) != os.path.join(self.json_dir, self.item_name, self.texture_folderName):
										shutil.copy(parm_result,os.path.join(self.json_dir, self.item_name, self.texture_folderName, copy))


					#print "parm name: %s"%parm
					#print "obj name: %s"%connect
					#print "parm val: %s"%value
				except:
					continue


			self.mini_items = self.settings(object_name, object_parm, connections)
			self.items[object_input_label] = self.mini_items

		#add description
		self.items["description"] = self.description

		#remove non usables
		try:
			folder_has = []
			for file_name in os.listdir(os.path.join(self.json_dir, self.item_name, self.texture_folderName)):
				folder_has.append(file_name)

			remove_list = [x for x in folder_has if x not in collect_texture_files]
			if len(remove_list) > 0:
				for rem in remove_list:
					os.remove(os.path.join(self.json_dir, self.item_name, self.texture_folderName, rem))
			#remove icons
			folder_has = []
			for file_name in os.listdir(os.path.join(self.json_dir, self.item_name, self.textureIcon_folderName)):
				folder_has.append(file_name)
			remove_list = [x for x in folder_has if x not in collect_texture_files]
			if len(remove_list) > 0:
				for rem in remove_list:
					os.remove(os.path.join(self.json_dir, self.item_name, self.textureIcon_folderName, rem))

		except:
			pass


		return self.items
		


	def settings(self, object_name, object_parm, object_connections):
		objects = {
					"name" : object_name,
					"connection" : object_connections,
					"parms" : object_parm
		}

		return objects


	def SaveAsJson(self):
		root = os.path.join(self.json_dir, self.item_name)
		if not os.path.isdir(root):
			os.makedirs(root)
		with open(os.path.join(root, self.item_name + self.material_extension), "w") as f:
			json.dump(self.items, f, indent=4)


	def SaveRenderView(self):
		destination = os.path.join(self.json_dir, self.item_name, self.displayImg_folderName)
		if not os.path.isdir(destination):
			os.makedirs(destination)
		cmds.setAttr('defaultRenderGlobals.imageFormat', 32)
		editor = 'renderView'
		img_file = os.path.join(destination, self.item_name)
		cmds.renderWindowEditor(editor, e=True, writeImage = img_file, colorManage=True)

		icon_source_path = os.path.join(destination, self.item_name + self.image_extension)
		icon_destination_path = os.path.join(self.json_dir, self.item_name, self.item_name + "_icon" + self.image_extension)
		self.IconGenerate(icon_source_path, icon_destination_path)
		

	def IconGenerate(self, source_path, destination_path):
		img = om.MImage()
		img.readFromFile(source_path)
		img.resize(200, 200, True)
		img.writeToFile(destination_path, 'png')



class ReadFiles():
	def __init__(self, item, material_dir, material_extension):
		self.read_items = self.ReadFromJson(material_dir, item, material_extension)
		self.CreateNodes()


	def ReadFromJson(self, material_dir, item, material_extension):
		destination = os.path.join(material_dir, item + material_extension)

		with open(destination, "r") as f:
			data = json.load(f)

		return data


	def CreateNodes(self):
		data = {}
		orig_SG_name = None
		for keys,vals in self.read_items.items():
			if keys != 'description':
				create_node = cmds.shadingNode(vals["name"], n=keys, asShader=True)
				if vals["name"] == "shadingEngine":
					orig_SG_name = create_node
				data[keys] = create_node
				for i in vals["parms"]:
					p = vals["parms"][i]
					if isinstance(p, list):
						if len(p) == 2:
							val = p[0]
							cmds.setAttr('{}.{}'.format(create_node, i), val[0], val[1], type="double2")

						if len(p) == 3:
							val = p[0]
							cmds.setAttr('{}.{}'.format(create_node, i), val[0], val[1], val[2], type="double3")

					elif isinstance(p, basestring):
						val = p
						cmds.setAttr('{}.{}'.format(create_node, i), val, type="string")

					elif p == "" or p == "null":
						pass

					elif isinstance(p, int) or isinstance(p, float):
						val = p
						cmds.setAttr('{}.{}'.format(create_node, i), val)




		for keys,vals in self.read_items.items():
			if keys != 'description':
				if vals["connection"]:
					for v in vals["connection"]:
						for items,values in v.items():
							input_name = items
							output_name = values
							if "." in items:
								input_name = "".join(items.split(".")[0])
							if "." in values:
								output_name = "".join(values.split(".")[0])
							for d in data.keys():
								if input_name == d:
									items = items.replace(input_name, data[d])
								if output_name == d:
									values = values.replace(output_name, data[d])
							if not "defaultColorMgtGlobals" in values and not "expression" in values:
								cmds.connectAttr(values,items)


		#Create Light Link
		light_list = ["RedshiftDomeLight", "RedshiftIESLight", "RedshiftPortalLight", "RedshiftPhysicalLight"]

		defaultMaya_lights = cmds.ls(lights=True)
		get_lights = [x for x in cmds.ls() if cmds.objectType(x) in light_list]

		get_lights += defaultMaya_lights
		light_list = cmds.listRelatives(get_lights, parent=True, fullPath=True)
		try:
			for light in light_list:
				cmds.lightlink(o=orig_SG_name, l=light)
		except:
			pass


		#Create Partitions
		cmds.partition(orig_SG_name, add='renderPartition')
	

class InfoTabMaya():
	def __init__(self, destination, renderer, CategoryPath, category_name, item, textureIcon_folderName):
		self.destination = destination
		self.CategoryPath = CategoryPath
		self.category_name = category_name
		self.item = item
		self.textureIcon_folderName = textureIcon_folderName
		self.renderer = renderer
		self.GenerateTabInfo()


	def GenerateTabInfo(self):
		parm_path = appdata_path = os.path.join(os.path.expandvars(r'%LOCALAPPDATA%'),'MatLib')
		if self.renderer == 'Redshift':
			parm_name = 'RS_Parms.json'
		elif self.renderer == 'Arnold':
			parm_name = 'mtoa_Parms.json'
		elif self.renderer == 'Vray':
			parm_name = 'vray_Parms.json'

		context_path = os.path.join(parm_path, parm_name)

		with open(context_path, 'r') as f:
			context_data = json.load(f)


		tiling_mode = None
		seq_mode = None

		collect_items = []
		seqandtile = []

		matinfo = []

		obj = json.load(open(self.destination))

		for keys,vals in obj.items():
			for v in vals:
				if "parms" in v:
					for i in vals["parms"].values():
						udim = "False"
						seq = "False"
						count = 0
						if isinstance(i, basestring) and os.path.exists(i):
							file_name = os.path.basename(i)

							tiling_mode = vals["parms"].get("uvTilingMode")

							if tiling_mode > 0 :
								udim = "True"

							seq_mode = vals["parms"].get("useFrameExtension")
							if seq_mode > 0:
								seq = "True"

							if any(k.isdigit() for k in file_name):
								flat_name = file_name.split('.')[0]
								flat_name = ''.join([x for x in flat_name if not x.isdigit()])
								udim_collect = [z for z in os.listdir(os.path.dirname(i)) if flat_name in z]
								count = len(udim_collect)

							re_path = os.path.join(self.CategoryPath, self.category_name, self.item, self.textureIcon_folderName, file_name)
							collect_items.append(re_path)

							c = {"seq" : seq, "udim" : udim, "count" : count}
							seqandtile.append(c)

			#material info
			if not "description" in keys:
				#test
				for n,nv in context_data.items():
					if obj[keys]["name"] == n:
						info_collect = {}
						info_collect["material_name"] = n
						for m_name,vs in nv.items():
							if vs["value"] == 1:
								info_collect[vs["name"]] = vals["parms"].get(m_name)


						print_data = self.MaterialInfoTab(**info_collect)
						matinfo.append(print_data)


			if keys == "description":
				description = obj["description"]


		return matinfo, collect_items, seqandtile, description


	def MaterialInfoTab(self , **info_collect):
		#mesh_FrNTypes = ["IOR(Advanced)", "Color + Edge Tint", "Metalness", "IOR"]
		#mesh_RflTypes = ["Glossiness", "Rougness"]
		#brdf_Types = ["Beckmann (Cook-Toorence)", "GGX", "Ashikhmin-Shirley"]
		#mode_Types = ["Color", "Temperature"]

		mesh_data = OrderedDict()

		mesh_data["MATERIAL"] = info_collect.get("material_name")

		for k,v in info_collect.items():
			if k != "material_name":
				mesh_data[k] = v

		return mesh_data



class ImageProcess():
	def __init__(self, from_file, item, destination, icon_path, image_extension, replc, source):
		self.from_file = from_file
		self.item = item
		self.icon_path = icon_path
		self.destination = destination
		self.source = source
		self.image_extension = image_extension
		self.replace = replc
		self.SaveRenderView()


	def SaveRenderView(self):
		#Add image from file
		if self.replace == -1 and self.from_file == 1:
			icon_source_path = os.path.join(self.icon_path, self.item + self.image_extension)
			icon_destination_path = os.path.join(self.icon_path, self.item + "_icon" + self.image_extension)
			self.IconGenerate(icon_source_path, icon_destination_path)

		#Add image from renderview
		elif self.replace == -1 and self.from_file == -1:
			self.RenderViewImg(ignore=-1)

		#Replace image from file
		elif self.replace == 1 and self.from_file == 1:
			self.IconGenerate(self.source,os.path.join(self.destination, self.item + self.image_extension))
			icon_source_path = os.path.join(self.destination, self.item + self.image_extension)
			icon_destination_path = os.path.join(self.icon_path, self.item + "_icon" + self.image_extension)
			self.IconGenerate(icon_source_path, icon_destination_path)

		#Replace image from renderview
		elif self.replace == 1 and self.from_file == -1:
			self.RenderViewImg(ignore=1)
			icon_source_path = os.path.join(self.destination, self.item + self.image_extension)
			icon_destination_path = os.path.join(self.icon_path, self.item + "_icon" + self.image_extension)
			self.IconGenerate(icon_source_path, icon_destination_path)


	def RenderViewImg(self, ignore):
		cmds.setAttr('defaultRenderGlobals.imageFormat', 32)
		editor = 'renderView'
		img_file = os.path.join(self.destination, self.item + self.image_extension)

		if os.path.exists(img_file) and ignore == -1:
			count = 1
			for i in os.listdir(self.destination):
				if self.item in i:
					count += 1
			img_file = os.path.join(self.destination, self.item + str(count) + self.image_extension)

			cmds.renderWindowEditor(editor, e=True, writeImage = img_file, colorManage=True)

		elif os.path.exists(img_file) and ignore == 1:
			cmds.renderWindowEditor(editor, e=True, writeImage = img_file, colorManage=True)


	def IconGenerate(self, source_path, destination_path):
		img = om.MImage()
		img.readFromFile(source_path)
		if self.replace != 1:
			img.resize(200, 200, True)
		img.writeToFile(destination_path, 'png')


class RendererCheck():
	def AvaliableRenderer(self, supported_renderer):
		check = []
		for i in cmds.pluginInfo(query=True, listPlugins=True):
			if i == supported_renderer[0]:
				check.append('Arnold')
			elif i == supported_renderer[1]:
				check.append('Redshift')
			elif i == supported_renderer[2]:
				check.append('Vray')

		return check



