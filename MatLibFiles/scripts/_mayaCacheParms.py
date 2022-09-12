import maya.cmds as cmds
import sys
import json
from collections import OrderedDict

#root = os.path.abspath('C:/MatLib/')
root = os.path.join(os.path.expandvars(r'%LOCALAPPDATA%'),'MatLib')


def renderer(cur_renderer):
	rs_file = 'RS_Parms.json'
	mtoa_file = 'mtoa_Parms.json'
	vray_file = 'vray_Parms.json'

	sel = cmds.selectedNodes()

	if cur_renderer == 'Arnold':
		f_path = os.path.join(root, mtoa_file)
		k = False
		val = True
	elif cur_renderer == 'Redshift':
		f_path = os.path.join(root, rs_file)
		k = True
		val = True
	elif cur_renderer == 'Vray':
		f_path = os.path.join(root, vray_file)
		k = True
		val = True

	createfiles(sel=sel, f_path=f_path, k=k, val=val)


def createfiles(sel, f_path, k, val):
	matAttribs = OrderedDict()
	for s in sel:
		data = OrderedDict()
		attribs = cmds.listAttr(s, keyable=k, v=val)
		
		for attrib in attribs:
			if not attrib.endswith('R') and not attrib.endswith('G') and not attrib.endswith('B'):
				name = attrib
				mini_data = {}
				nice_name = cmds.attributeName(s + '.' + attrib, n=True)
				if not nice_name[-1].isdigit():
					mini_data['name'] = nice_name
					mini_data['value'] = 0

					data[name] = mini_data

		matAttribs[cmds.objectType(s)] = data


	with open(f_path, 'w') as f:
		json.dump(matAttribs, f, indent=4)

cur_renderer = input()
renderer(cur_renderer=cur_renderer)










