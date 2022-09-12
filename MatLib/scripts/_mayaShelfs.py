import maya.cmds as cmds
import os

main_path = os.path.dirname(os.path.abspath(__file__))
setup_path = os.path.abspath(os.path.join(main_path, os.pardir))
ui_path = os.path.join(setup_path, 'Ui')
ui_icon_path = os.path.join(ui_path, 'icons')

class customShelf():
	def __init__(self, iconPath= ""):
		self.name = "MatLib"
		self.iconPath = iconPath

		self.labelBackground = (0,0,0,0)
		self.labelColour = (.9,.9,.9)


		self._cleanOldShelf()
		cmds.setParent(self.name)
		self.build()

	def addButon(self, label, icon=None, command="", doubleCommand=""):
		cmds.setParent(self.name)
		cmds.shelfButton(width=37, height=37, image=icon, l=label, command=command, dcc=doubleCommand, imageOverlayLabel="", olb=self.labelBackground, olc=self.labelColour)


	def _cleanOldShelf(self):
		if cmds.shelfLayout(self.name, ex=1):
			if cmds.shelfLayout(self.name, q=1, ca=1):
				for each in cmds.shelfLayout(self.name, q=1, ca=1):
					cmds.deleteUI(each)

		else:
			cmds.shelfLayout(self.name, p="ShelfLayout")

	def build(self):
		cmd = """
from MatLib import MainWindow 
MainWindow().show()
		"""
		icon = os.path.join(ui_icon_path, 'MLibraryIcon.svg')
		self.addButon(label="Material Library", icon=icon, command=cmd)

		cmd = """
from _mayaReset import ResetWindow
ResetWindow().show()
		"""
		icon = os.path.join(ui_icon_path, 'MPathReset.svg')
		self.addButon(label="Reset Paths", icon=icon, command=cmd)

		cmd = """
from _textureTransfer import TextureTransferWindow
TextureTransferWindow().show()
		"""
		icon = os.path.join(ui_icon_path, 'MTransferIcon.svg')
		self.addButon(label="Transfer to Project", icon=icon, command=cmd)

