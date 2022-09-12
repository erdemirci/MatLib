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
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from collections import OrderedDict
import os
import sys
import json
import shutil
import time
from PySide2 import QtWidgets, QtCore, QtUiTools, QtGui
import webbrowser
import base64
import _maya
import importlib
#importlib.reload(_maya)
import _transfer
#reload(_transfer)
from _maya import SaveFiles, ReadFiles, InfoTabMaya, ImageProcess, RendererCheck
from _transfer import TransferWindow
import _version
#reload(_version)
import _color
#reload(_color)
import _editMaterial
#reload(_editMaterial)
from _editMaterial import MaterialDisplay


main_path = os.path.dirname(os.path.abspath(__file__))
setup_path = os.path.abspath(os.path.join(main_path, os.pardir))
ui_path = os.path.join(setup_path, 'Ui')
#file_path = os.path.join(setup_path, 'files')
ui_icon_path = os.path.join(ui_path, 'icons')
appdata_path = os.path.join(os.path.expandvars(r'%LOCALAPPDATA%'),'MatLib')
config_path = os.path.join(appdata_path, 'config.json')
supported_renderers = ['Redshift','Arnold','Vray']
category_folderName = "categories"
material_folderName = "materials"
texture_folderName = "textures"
textureIcon_folderName = "texture_icons"
displayImg_folderName = "images"
image_extension = ".png"
material_extension = ".json"
app = "Maya"

rep_name = 'MatLib_Repository'
filetype = '*.jpg *.jpeg *.png *.tif'

version = sys.version_info.major

if version == 3:
    long = int
    basestring = str

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, callback=None):

        for entry in QtWidgets.QApplication.allWidgets():
            try:
                if entry.objectName() == MainWindow:
                    entry.close()
            except (AttributeError, TypeError):
                pass
        parent = maya_main_window()

        super(MainWindow, self).__init__(parent=parent)

        self.setContentsMargins(QtCore.QMargins(0,0,0,0))
        ui_file = os.path.join(ui_path, 'Matlib.ui')
        self.ui = QtUiTools.QUiLoader().load(ui_file, parentWidget=self)
        self.setWindowTitle('MatLib %s' %_version.__version__)
        self.setWindowIcon(QtGui.QIcon(os.path.join(ui_icon_path, 'MatlibLogoNS_small.svg')))

        self.thumbnailSize = 180

        #Widget Setup
        self.MaterialIconListView = QtWidgets.QListWidget()
        self.MaterialIconListView.setViewMode(QtWidgets.QListWidget.IconMode)
        self.MaterialIconListView.setMovement(QtWidgets.QListView.Static)
        self.MaterialIconListView.setResizeMode(QtWidgets.QListView.Adjust)
        self.MaterialIconListView.setSpacing(5)
        self.MaterialIconListView.setSortingEnabled(True)

        self.ui.tabtreewidget.setIconSize(QtCore.QSize(100,100))
        self.ui.treeWidget.setSortingEnabled(True)

        self.ui.treeWidget.setColumnCount(1)
        self.ui.treeWidget.setHeaderLabel('CATEGORIES')
        self.ui.treeWidget.header().setDefaultAlignment(QtGui.Qt.AlignHCenter|QtGui.Qt.AlignVCenter)


        self.current_item = QtWidgets.QLabel("0/0")
        self.current_item.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.imageshow_layout.addWidget(self.current_item)

        self.formlayout = QtWidgets.QFormLayout()

        self.groupBox = QtWidgets.QGroupBox()
        self.groupBox.setLayout(self.formlayout)

        self.infoscrollArea = QtWidgets.QScrollArea()
        self.infoscrollArea.setWidget(self.groupBox)
        self.infoscrollArea.setWidgetResizable(True)


        self.ui.largeimg_area.setFocusPolicy(QtCore.Qt.NoFocus)
        self.ui.tabtreewidget.setFocusPolicy(QtCore.Qt.NoFocus)

        #password layout
        self.pwd_dialog = QtWidgets.QDialog(self)
        self.pwd_dialog.setWindowTitle('Comfirm Password')
        pwd_layout = QtWidgets.QVBoxLayout()
        pwd_form_layout = QtWidgets.QFormLayout()
        info_label = QtWidgets.QLabel('Repository is password protected.')
        pwd_label = QtWidgets.QLabel('Password:')
        self.pwd_pass = QtWidgets.QLineEdit()
        self.pwd_pass.setEchoMode(QtWidgets.QLineEdit.Password)

        pwd_form_layout.addRow(pwd_label, self.pwd_pass)

        self.pwd_button = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel, self.pwd_dialog)

        pwd_layout.addWidget(info_label)
        pwd_layout.addLayout(pwd_form_layout)
        pwd_layout.addWidget(self.pwd_button)
    
        self.pwd_dialog.setLayout(pwd_layout)
        self.pwd_button.accepted.connect(self.pwd_dialog.accept)
        self.pwd_button.rejected.connect(self.pwd_dialog.reject)

        #MenuBar
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('Repository')
        transferMenu = menuBar.addMenu('Transfer')
        helpMenu = menuBar.addMenu('Help')


        fileMenu_linkRepository = QtWidgets.QAction(QtGui.QIcon(os.path.join(ui_icon_path, 'M_Link.svg')), 'Link Repository', self)
        fileMenu.addAction(fileMenu_linkRepository)
        fileMenu_unlinkRepository = QtWidgets.QAction(QtGui.QIcon(os.path.join(ui_icon_path, 'M_BrokenLink.svg')), 'Unlink Repository', self)
        fileMenu.addAction(fileMenu_unlinkRepository)
        fileMenu_createRepository = QtWidgets.QAction(QtGui.QIcon(os.path.join(ui_icon_path , 'M_CreateRepo.svg')), 'Create Repository', self)
        fileMenu.addAction(fileMenu_createRepository)
        fileMenu_deleteRepository = QtWidgets.QAction(QtGui.QIcon(os.path.join(ui_icon_path, 'M_DeleteRepo.svg')), 'Delete Repository', self)
        fileMenu.addAction(fileMenu_deleteRepository)

        fileTranferReptoRep = QtWidgets.QAction(QtGui.QIcon(os.path.join(ui_icon_path, 'M_Transfer.svg')), 'Transfer Materials', self)
        transferMenu.addAction(fileTranferReptoRep)
        helpMenuOnlineDoc = QtWidgets.QAction(QtGui.QIcon(os.path.join(ui_icon_path, 'M_Docs.svg')), 'Documentation', self)
        helpMenu.addAction(helpMenuOnlineDoc)

        self.ui.comboBox_2.addItem('Redshift')
        self.ui.comboBox_2.addItem('Arnold')
        self.ui.comboBox_2.addItem('Vray')
        
        #STYLESHEET SETUP
        self.MaterialIconListView.setStyleSheet("QListWidget::item {"
                                                "border-style : outset;"
                                                "border-width : 1px;"
                                                "border-color : black;"
                                                "border-radius : 8px;"
                                                "background: #33373B;"
                                                "}"
                                                "QListWidget QScrollBar"
                                                "{"
                                                "background: #33373B;"
                                                "}"
                                                "QListView::item::selected {"
                                                "border-style : solid;"
                                                "border-width : 1px;"
                                                "border-color : %s;"
                                                "background : %s;"
                                                "}" %(_color.__bordercolor__, _color.__selectedbackground__)
                                                )

        self.ui.treeWidget.header().setStyleSheet("QHeaderView::section {"
                                                "background-color : qlineargradient(x1:0, y1:0, x2:0, y2:1,"
                                                "stop:0 #616161, stop: 0.2 %s,"
                                                "stop: 0.3 #434343, stop:1 %s);"
                                                "font : Arial;"
                                                "font-size : 15px;"
                                                "border-style : plain;"
                                                "color : %s;"
                                                "}" %(_color.__background__, _color.__background__ ,_color.__titlecolor__)
                                                )

        self.ui.treeWidget.setStyleSheet("QTreeView {"
                                        "background-color : %s;"
                                        "border-style : outset;"
                                        "border-width : 0px;"
                                        "border-radius : 4px;"
                                        "padding : 1px;"
                                        "font : Arial;"
                                        "font-size : 20px"
                                        "}"
                                        "QTreeView::item:selected {"
                                        "background : %s;"
                                        "}" %(_color.__background__, _color.__selectedbackground__)
                                        )

        self.ui.desc_label.setStyleSheet("color : %s;"
                                        %(_color.__titlecolor__)
                                        )


        self.current_item.setStyleSheet("QLabel {"
                                            "font-size : 15pt;"
                                            #"background-color : #88000000"
                                            "}"
                                            )


        self.ui.scrollArea.setStyleSheet("background-color : %s;"
                                        "border-style : plain;"
                                        "border-width : 1px;"
                                        "border-radius : 6px;"
                                        "padding : 1px;"
                                         %(_color.__background__)
                                        )

        self.ui.search_lineEdit.setStyleSheet(
                                        "selection-background-color : %s;"
                                        %(_color.__borderhighlight__)
                                        )

        self.ui.lineEdit.setStyleSheet(
                                        "selection-background-color : %s;"
                                        %(_color.__borderhighlight__)
                                        )

        self.setStyleSheet("""
            QMenuBar::item::selected {
                background-color : %s;
            }
            QMenu::item::selected {
                background-color : %s;
            }
            QComboBox QAbstractItemView {
                selection-background-color : %s;
            }
            QListView::item:selected {
                selection-background-color : %s;
            }
            """ %(_color.__selectedbackground__, _color.__selectedbackground__, _color.__selectedbackground__, _color.__selectedbackground__))

        self.ui.pushButton_3.setStyleSheet(
                                        "background-color : %s;"
                                        "color : #141414;"
                                        "border-color : %s;"
                                        %(_color.__buttoncolor__, _color.__buttoncolor__)
                                            )

        self.ui.comboBox_2.setStyleSheet(
                                        """
                                        QComboBox:disabled {
                                            color : white;
                                            font-weight : 200;
                                        }
                                        """
                                        )



        #initial variables
        self.CategoryPath = None
        self.main = None
        self.submit_counter = 0
        self.password = "123admin"
        self.catdialog = None
        self.current_path = None
        self.pass_val = False
        #self.renderer = self.ui.comboBox_2.itemText(0)
        self.renderer = None
        
        self.avaliable_renderer = self.LoadRenderer()
        self.ConfigLoad()
        self.GenerateCategories()
        self.CategoryStyleChange()
        self.ui.treeWidget.setMinimumSize(200,0)
        self.ui.treeWidget.setMaximumSize(0,1200)

        self.ui.img_leftButton.setIcon(QtGui.QIcon(os.path.join(ui_icon_path, 'M_LeftArrow.svg')))
        self.ui.img_rightButton.setIcon(QtGui.QIcon(os.path.join(ui_icon_path, 'M_RightArrow.svg')))

        self.ui.pushButton.setIcon(QtGui.QIcon(os.path.join(ui_icon_path, 'M_AddCat.svg')))
        self.ui.pushButton.setIconSize(QtCore.QSize(28,28))

        self.ui.pushButton_2.setIcon(QtGui.QIcon(os.path.join(ui_icon_path, 'M_RemoveCat.svg')))
        self.ui.pushButton_2.setIconSize(QtCore.QSize(28,28))

        #Connections
        self.ui.pushButton.clicked.connect(self.AddToCategories)
        self.ui.pushButton_2.clicked.connect(self.RemoveFromCategories)
        self.ui.pushButton_3.clicked.connect(self.ImportMaterial)
        self.ui.addMaterial.clicked.connect(self.AddMaterial)
        self.ui.delMaterial.clicked.connect(self.RemoveMaterial)
        self.ui.treeWidget.itemSelectionChanged.connect(self.GenerateMaterialList)
        self.ui.search_lineEdit.textChanged.connect(self.MaterialSearch)
        self.MaterialIconListView.clicked.connect(self.LargeImageDisplay)
        self.MaterialIconListView.clicked.connect(self.InfoTab)
        self.ui.addImageFromFile.clicked.connect(self.EditTab_AddImageFromFile)
        self.ui.pushButton_4.clicked.connect(self.EditTab_AddImageFromRenderView)
        self.ui.pushButton_5.clicked.connect(self.EditTab_ReplaceImageFromFile)
        self.ui.pushButton_6.clicked.connect(self.EditTab_ReplaceImageFromRenderView)
        self.ui.pushButton_7.clicked.connect(self.EditTab_ReplaceDescription)
        self.ui.pushButton_8.clicked.connect(self.EditTab_RemoveImage)
        self.ui.pushButton_9.clicked.connect(self.on_editclick)

        self.ui.img_leftButton.clicked.connect(lambda : self.Submit(act=0))
        self.ui.img_rightButton.clicked.connect(lambda : self.Submit(act=1))
        
        self.MaterialIconListView.currentItemChanged.connect(self.ItemChanged)
        self.ui.comboBox.currentIndexChanged.connect(self.UpdateRepository)

        #Menu Bar connect
        fileMenu_createRepository.triggered.connect(self.CreateRepository)
        fileMenu_deleteRepository.triggered.connect(self.DeleteRepository)
        fileMenu_linkRepository.triggered.connect(self.LinkRepository)
        fileMenu_unlinkRepository.triggered.connect(self.UnLinkRepository)

        fileTranferReptoRep.triggered.connect(self.on_transferclick)
        helpMenuOnlineDoc.triggered.connect(lambda: webbrowser.open('https://matlib.readthedocs.io/en/latest/index.html'))

        self.ui.comboBox_2.currentIndexChanged.connect(self.RendererChange)

        self.ui.scrollArea.setWidget(self.MaterialIconListView)

        self.dialog = TransferWindow(self, config_path, app, self.renderer, category_folderName)
        self.dialog.export_button.clicked.connect(self.GenerateMaterialList)

        self.matdisplay = MaterialDisplay(self, self.renderer)
        self.matdisplay.button.clicked.connect(self.InfoTab)

        




    def CategoryStyleChange(self):
        index = self.ui.comboBox.currentIndex()
        if index > 0 :
            self.ui.comboBox.setStyleSheet('''
                                        QComboBox:!editable, QComboBox::drop-down:editable {
                                            background-color : %s;
                                            color : black;
                                        }
                                        QComboBox:!editable:on, QComboBox::drop-down:editable:on {
                                            color : black;
                                        }
                                        QComboBox:editable {
                                            color : black;
                                        }
                                            '''%(_color.__titlecolor__))


        else:
            self.ui.comboBox.setStyleSheet('''
                                        QComboBox:!editable {
                                            background-color : %s;
                                            color : white;
                                        }
                                            '''%(_color.__background__))



    def ConfigLoad(self):
        with open(config_path, "r") as f:
            file_data = json.load(f)
        if len(file_data[app][self.renderer]["repository"]) > 0:
            if file_data[app][self.renderer]["repository"][0] != 'Default Repository':
                category_path = self.FirstTime()
                file_data[app][self.renderer]["current_index"] = 0
                file_data[app][self.renderer]["dirs"].insert(0, category_path)
                file_data[app][self.renderer]["repository"].insert(0, "Default Repository")
                open(config_path, "w").write(json.dumps(file_data,indent=4))

        for idx,item in enumerate(file_data[app][self.renderer]["dirs"]):
            if not os.path.exists(item):
                file_data[app][self.renderer]["dirs"].pop(idx)
                file_data[app][self.renderer]["repository"].pop(idx)
                file_data[app][self.renderer]["current_index"] = 0
                open(config_path, "w").write(json.dumps(file_data,indent=4))
                category_index = 0
            elif os.path.exists(item) and len(file_data[app][self.renderer]['dirs'])-1 > file_data[app][self.renderer]['current_index']:
                file_data[app][self.renderer]["current_index"] = 0
                open(config_path, "w").write(json.dumps(file_data,indent=4))


        category_index = file_data[app][self.renderer]["current_index"]

        while True:
            
            try:
                category_path = file_data[app][self.renderer]["dirs"][category_index]
                break
            except:
                creation_path = self.FirstTime()
                for renderer in supported_renderers:
                    file_data[app][renderer]["dirs"] = [creation_path]
                    file_data[app][renderer]["repository"] = ["Default Repository"]
                    file_data[app][renderer]["current_index"] = 0
                    open(config_path, "w").write(json.dumps(file_data, indent=4))


        repository_items = file_data[app][self.renderer].get("repository")
        for rep in repository_items:
            self.ui.comboBox.addItem(rep)

        self.ui.comboBox.setCurrentIndex(category_index)

        self.current_path = category_path
        self.CategoryPath = os.path.join(category_path, app, self.renderer, category_folderName)


    def LoadRenderer(self):
        plugins = ['mtoa', 'redshift4maya', 'vrayformaya']
        avaliable_renderer = RendererCheck().AvaliableRenderer(plugins)
        if len(avaliable_renderer) > 1:
            false_idxs = [supported_renderers.index(x) for x in supported_renderers if x not in avaliable_renderer]
            true_idxs = [supported_renderers.index(x) for x in supported_renderers if x in avaliable_renderer]
            self.renderer = self.ui.comboBox_2.itemText(min(true_idxs))
            self.ui.comboBox_2.setCurrentIndex(min(true_idxs))
            #self.ui.comboBox_2.setDisabled(False)
            for i in false_idxs:
                self.ui.comboBox_2.model().item(i).setEnabled(False)
        elif len(avaliable_renderer) == 1 and avaliable_renderer[0] == 'Redshift': 
            self.renderer = self.ui.comboBox_2.itemText(0)
            self.ui.comboBox_2.setCurrentIndex(0)
            self.ui.comboBox_2.setDisabled(True)
        elif len(avaliable_renderer) == 1 and avaliable_renderer[0] == 'Arnold':
            self.renderer = self.ui.comboBox_2.itemText(1)
            self.ui.comboBox_2.setCurrentIndex(1)
            self.ui.comboBox_2.setDisabled(True)
        elif len(avaliable_renderer) == 1 and avaliable_renderer[0] == 'Vray':
            self.renderer = self.ui.comboBox_2.itemText(2)
            self.ui.comboBox_2.setCurrentIndex(2)
            self.ui.comboBox_2.setDisabled(True)
        else:
            self.renderer = None
            QtWidgets.QMessageBox.about(self, 'Error', 'There are no supported plugins avaliable.\n Make sure either Redshift,Vray or Arnold plugin is active.')
            sys.exit()

        return avaliable_renderer

    def FirstTime(self):
        repository_file = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Directory', options=QtWidgets.QFileDialog.ShowDirsOnly))
        if not repository_file:
            sys.exit()
        else:
            if os.path.basename(repository_file) == rep_name:
                repository_file = os.path.abspath(os.path.join(repository_file, os.pardir))

            for renderer in supported_renderers:
                root = '{}/{}/{}/{}'.format(rep_name, app, renderer, category_folderName)
                collect = []

                for files in os.listdir(repository_file):
                    if files == rep_name:
                        for c_root, dirs, files in os.walk(os.path.join(repository_file, files, app, renderer)):
                            for d in dirs:
                                collect.append(d)

                            if len(collect) == 1:
                                break

                if len(collect) < 1 :
                    path = os.path.join(repository_file, root)
                    os.makedirs(path)
        
            return os.path.normpath(os.path.join(repository_file, 'MatLib_Repository'))


    def RendererChange(self):
        index = self.ui.comboBox_2.currentIndex()
        rep_index = self.ui.comboBox.currentIndex()
        self.renderer = self.ui.comboBox_2.itemText(index)
        self.dialog = TransferWindow(self, config_path, app, self.renderer, category_folderName)
        self.dialog.export_button.clicked.connect(self.GenerateMaterialList)
        self.matdisplay = MaterialDisplay(self, self.renderer)
        self.matdisplay.button.clicked.connect(self.InfoTab)
        self.UpdateRepository(rep_index)


    def MaterialSearch(self, text):
        for cur_item in range(self.MaterialIconListView.count()):
            cur_it = self.MaterialIconListView.item(cur_item)
            if text.lower() in cur_it.text().lower():
                cur_it.setHidden(0)
            else:
                cur_it.setHidden(1)


    def GenerateCategories(self):
        destination = os.path.abspath(self.CategoryPath)
        for i in os.listdir(destination):
            QtWidgets.QTreeWidgetItem(self.ui.treeWidget, [i])


    def AddToCategories(self):
        text, ok = QtWidgets.QInputDialog.getText(self, 'Add Category', 'Category Name')
        if ok:
            if len(text) == 0:
                QtWidgets.QMessageBox.about(self, 'Error', 'Category Name must be greater than 1 character.')
            else:
                destination = os.path.join(self.CategoryPath, text.upper())
                if not os.path.isdir(destination):
                    os.makedirs(destination)
                    QtWidgets.QTreeWidgetItem(self.ui.treeWidget,[text.upper()])
                else:
                    QtWidgets.QMessageBox.about(self, 'Error', '{} already exists in this repository.'.format(text.upper()))


    def RemoveFromCategories(self):
        if not self.ui.treeWidget.selectedItems():
            QtWidgets.QMessageBox.about(self, 'Error', 'Select an item from Categories.')
        else:
            run = 0
            pwd_data = self.PasswordCheck()
            if pwd_data['pass_use'] == 'False':
                run = 1
            elif pwd_data['pass_use'] == 'True':
                pwd_ok = self.pwd_dialog.exec_()

                if pwd_ok == QtWidgets.QDialog.Accepted and base64.b64decode(pwd_data['password']).decode('utf-8') == self.pwd_pass.text():
                    run = 1
                elif pwd_ok == QtWidgets.QDialog.Rejected:
                    run = -1

            if run == 1:
                text,ok = QtWidgets.QInputDialog.getText(self, 'Confirm Delete', 'Are you sure? This action cannot be undone. \n'
                                                        'Type "YES" to confirm deletion')
                if text == "YES" and ok:
                    index = self.ui.treeWidget.selectedIndexes()[0]
                    item = self.ui.treeWidget.itemFromIndex(index).text(0)

                    #Delete from Category List
                    root = self.ui.treeWidget.invisibleRootItem()
                    for i in self.ui.treeWidget.selectedItems():
                        (i.parent() or root).removeChild(i)

                    #Delete from folder
                    file_path = os.path.join(self.CategoryPath, item)
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
            elif run == 0:
                QtWidgets.QMessageBox.about(self, 'Error', 'Password is incorrect.Please try again.')
                self.RemoveFromCategories()


    def AddMaterial(self):
        editor = 'renderView'
        if not self.ui.treeWidget.selectedItems():
            QtWidgets.QMessageBox.about(self, 'Error', 'Select an item from Categories.')
        elif cmds.selectedNodes() == None:
            QtWidgets.QMessageBox.about(self, 'Error', 'Select a Shading Group(SG).')
        elif not cmds.objectType(cmds.selectedNodes()[0]) == 'shadingEngine':
            QtWidgets.QMessageBox.about(self, 'Error', 'Shader selection error.\nMake sure the selected node is "Shading Group(SG)".\nMake sure to select a single node.')
        elif len(cmds.selectedNodes()) > 1:
            QtWidgets.QMessageBox.about(self, 'Error', 'Multiple Nodes are selected\nMake sure the selected node is "Shading Group(SG).')
        elif cmds.renderWindowEditor(editor, q=True, nbImages=True) + 1 == 0:
            QtWidgets.QMessageBox.about(self, 'Render View', 'There is no rendered image in MAYA RenderView.\n{} RenderView is not supported.'.format(self.renderer))
        elif not cmds.getAttr('defaultRenderGlobals.currentRenderer') == self.renderer.lower():
            QtWidgets.QMessageBox.about(self, 'Render View', 'Current renderer is not {}.'.format(self.renderer))
        else:
            index = self.ui.treeWidget.selectedIndexes()[0]
            item = self.ui.treeWidget.itemFromIndex(index).text(0)
            destination = os.path.abspath(self.CategoryPath)

            material_dialog = QtWidgets.QDialog()
            material_dialog.setWindowTitle('Material Information')
            material_dialog.setWindowIcon(QtGui.QIcon(os.path.join(ui_icon_path, 'MatlibLogoNS_small.svg')))
            material_name = QtWidgets.QLineEdit(material_dialog)
            material_description = QtWidgets.QLineEdit(material_dialog)
            material_button = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel, material_dialog)

            layout = QtWidgets.QFormLayout(material_dialog)
            layout.addRow('Material Name:', material_name)
            layout.addRow('Material Description', material_description)
            layout.addWidget(material_button)

            material_button.accepted.connect(material_dialog.accept)
            material_button.rejected.connect(material_dialog.reject)
            ok = material_dialog.exec_()
            text = material_name.text()
            dscpt = material_description.text()

            agreed = -1

            if ok == QtWidgets.QDialog.Accepted and len(text) == 0:
                QtWidgets.QMessageBox.about(self, 'Error', 'Material name is not defined.')
            if ok == QtWidgets.QDialog.Accepted and len(text) > 0:
                if os.path.exists(os.path.join(destination, item, text)):
                    reply = QtWidgets.QMessageBox.question(self, 'Existing File', '{} is already in the {}.\nDo you want to overwrite?'.format(text, item),
                                                            QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
                    if reply == QtWidgets.QMessageBox.Yes:
                        agreed = 1
                else:
                    agreed = 1

            if agreed == 1:
                _mayaSave = SaveFiles(cmds.selectedNodes(), self.renderer, text, dscpt, item, destination, material_folderName, texture_folderName, displayImg_folderName, image_extension, material_extension, textureIcon_folderName)
                self.GenerateMaterialList()


    def RemoveMaterial(self):
        if not self.MaterialIconListView.selectedItems():
            QtWidgets.QMessageBox.about(self, 'Error', 'Material is not selected.')
        else:
            run = 0
            pwd_data = self.PasswordCheck()
            if pwd_data['pass_use'] == 'False':
                run = 1
            elif pwd_data['pass_use'] == 'True':
                pwd_ok = self.pwd_dialog.exec_()

                if pwd_ok == QtWidgets.QDialog.Accepted and base64.b64decode(pwd_data['password']).decode('utf-8') == self.pwd_pass.text():
                    run = 1
                elif pwd_ok == QtWidgets.QDialog.Rejected:
                    run = -1

            if run == 1:
                text, ok = QtWidgets.QInputDialog.getText(self, 'Confirm Delete', 'Are you sure? This action cannot be undone.\n Type "YES" to confirm deletion.')
                if text == "YES":
                    item = self.MaterialIconListView.selectedItems()[0].text()
                    category_index = self.ui.treeWidget.selectedIndexes()[0]
                    category_name = self.ui.treeWidget.itemFromIndex(category_index).text(0)
                    destination = os.path.join(self.CategoryPath, category_name)
                    for files in os.listdir(destination):
                        if item in files:
                            file_path = os.path.join(destination, files)
                            if os.path.isfile(file_path) or os.path.islink(file_path):
                                os.unlink(file_path)
                            elif os.path.isdir(file_path):
                                shutil.rmtree(file_path)
                    self.GenerateMaterialList()
                    #self.pwd_dialog.close()
            elif run == 0:
                QtWidgets.QMessageBox.about(self, 'Error', 'Password is incorrect.Please try again.')
                self.RemoveMaterial()



    def GenerateMaterialList(self):
        try:
            index = self.ui.treeWidget.selectedIndexes()[0]
            item = self.ui.treeWidget.itemFromIndex(index).text(0)

            self.MaterialIconListView.clear()

            root = os.path.join(self.CategoryPath, item)
            if os.path.exists(root):
                for i in os.listdir(root):
                    icon_path = os.path.join(self.CategoryPath, item, i, i + "_icon" + image_extension)
                    mat = QtWidgets.QListWidgetItem(self.MaterialIconListView)

                    icon = QtGui.QIcon()
                    icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)

                    mat.setIcon(icon)

                    mat.setText(i)  
                    mat.setFont(QtGui.QFont('Arial', 10, QtGui.QFont.Bold))

                    

                    self.MaterialIconListView.setIconSize(QtCore.QSize(self.thumbnailSize, self.thumbnailSize))
 
        except IndexError:
            self.MaterialIconListView.clear()



    def LargeImageDisplay(self):
        if self.MaterialIconListView.selectedItems():
            try:
                item = self.MaterialIconListView.selectedItems()[0].text()
                category_index = self.ui.treeWidget.selectedIndexes()[0]
                category_name = self.ui.treeWidget.itemFromIndex(category_index).text(0)
                self.large_view = QtWidgets.QLabel("icon")
                name = QtWidgets.QLabel(item, self.large_view)
                name.setStyleSheet("QLabel {"
                                    "font-size : 30pt;"
                                    "background-color : #88000000"
                                    "}"
                                    )

                image_data = []
                root = os.path.join(self.CategoryPath, category_name, item, displayImg_folderName)
                for file in os.listdir(root):
                    file_path = os.path.join(root,file)
                    image_data.append(file_path)

                #put target_path at the begining
                target_path = os.path.join(root, item + image_extension)
                image_data.insert(0, image_data.pop(image_data.index(target_path)))

                min_val = 0
                max_val = len(image_data) - 1

                if self.submit_counter < min_val:
                    self.submit_counter = min_val
                if self.submit_counter > max_val:
                    self.submit_counter = max_val


                self.current_item.setText('%s/%s'%(self.submit_counter + 1, max_val + 1))
                pixmap = QtGui.QPixmap(image_data[self.submit_counter])
                pixmap.scaled(800, 800, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                self.large_view.setPixmap(pixmap.scaled(800,800, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
                self.large_view.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignCenter)
                self.large_view.setScaledContents(False)
                self.large_view.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
                self.large_view.setFocusPolicy(QtCore.Qt.NoFocus)
                
                self.ui.largeimg_area.setWidget(self.large_view)

            except IndexError:
                pass

            
    def Submit(self, act):
        sender = self.sender()
        if act == 1:
            self.submit_counter += 1   
        else:
            self.submit_counter -= 1

        self.LargeImageDisplay()


    def ItemChanged(self):
        self.submit_counter = 0


    def InfoTab(self):
        if self.MaterialIconListView.selectedItems():
            self.ui.tabtreewidget.clear()

            item = self.MaterialIconListView.selectedItems()[0].text()

            category_index = self.ui.treeWidget.selectedIndexes()[0]
            category_name = self.ui.treeWidget.itemFromIndex(category_index).text(0)

            destination = os.path.join(self.CategoryPath, category_name, item, item + material_extension)

            _mayaInfoTab = InfoTabMaya(destination, self.renderer, self.CategoryPath, category_name, item, textureIcon_folderName)

            matinfo = _mayaInfoTab.GenerateTabInfo()[0]
            collect_items = _mayaInfoTab.GenerateTabInfo()[1]
            seqandtile = _mayaInfoTab.GenerateTabInfo()[2]
            description = _mayaInfoTab.GenerateTabInfo()[3]


            self.ui.desc_out.setText(description)

            for collect in collect_items:
                self.main = QtWidgets.QTreeWidgetItem(self.ui.tabtreewidget, )
                first = self.main.setIcon(0, QtGui.QPixmap(collect))
                repath = collect.replace(textureIcon_folderName, texture_folderName)
                second = self.main.setText(1, repath)

                udim_c = "0"
                seq_c = "0"
                seqandtile_count = str(seqandtile[collect_items.index(collect)].get("count"))

                if seqandtile[collect_items.index(collect)].get("udim") == "True":
                    udim_c = seqandtile_count
                third = self.main.setText(2, seqandtile[collect_items.index(collect)].get("udim"))
                forth = self.main.setText(3, udim_c)
                if seqandtile[collect_items.index(collect)].get("seq") == "True":
                    seq_c = seqandtile_count
                fifth = self.main.setText(4, seqandtile[collect_items.index(collect)].get("seq"))
                sixth = self.main.setText(5, seq_c) 
                self.ui.tabtreewidget.setRootIsDecorated(0)

            #delete widgets
            while self.formlayout.count():
                child = self.formlayout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            for mat in matinfo:
                for i in mat.keys():
                    if i == 'MATERIAL':
                        parm_name = QtWidgets.QLabel('<font color = "{}">{}</font>'.format(_color.__titlecolor__, str(i)))
                    else:
                        parm_name = QtWidgets.QLabel('<font color = "{}">{}</font>'.format(_color.__buttoncolor__, str(i)))
                    if isinstance(mat[i], list):
                        mat[i] = ', '.join([str(k) for k in mat[i][0]])
                    self.formlayout.addRow(parm_name, QtWidgets.QLabel("{}".format(mat[i])))

                line = QtWidgets.QFrame()
                line.setMinimumWidth(2)
                line.setFixedHeight(10)
                line.setFrameShape(QtWidgets.QFrame.HLine)
                self.formlayout.addWidget(line)
                
            vertSpacer = QtWidgets.QSpacerItem(20,40,QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Expanding)
            
            self.infoscrollArea.setFocusPolicy(QtCore.Qt.NoFocus)
            self.ui.material_infolayout.addWidget(self.infoscrollArea)
            # #self.ui.material_infolayout.addItem(vertSpacer)


    def EditTab_AddImageFromFile(self):
        try:
            item = self.MaterialIconListView.selectedItems()[0].text()
            category_index = self.ui.treeWidget.selectedIndexes()[0]
            category_name = self.ui.treeWidget.itemFromIndex(category_index).text(0)
            image_path,image_type = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Image', filter=filetype)


            if os.path.isfile(image_path):
                destination = os.path.join(self.CategoryPath, category_name, item, displayImg_folderName)
                shutil.copy(os.path.abspath(image_path), destination)
                self.LargeImageDisplay()

        except IndexError:
            QtWidgets.QMessageBox.about(self, 'Index Error', 'Material is not selected.')


    def EditTab_AddImageFromRenderView(self):
        try:
            item = self.MaterialIconListView.selectedItems()[0].text()
            category_index = self.ui.treeWidget.selectedIndexes()[0]
            category_name = self.ui.treeWidget.itemFromIndex(category_index).text(0)
            destination = os.path.join(self.CategoryPath, category_name, item, displayImg_folderName)
            icon_path = None
            source_path = None
            from_file = -1
            replc = -1
            if not os.path.isdir(destination):
                QtWidgets.QMessageBox.about(self, 'Error', 'Create the material first')
            else:
                _mayaImgPrcs = ImageProcess(from_file, item, destination, icon_path, image_extension, replc, source_path)
                self.LargeImageDisplay()

        except IndexError:
            QtWidgets.QMessageBox.about(self, 'Index Error', 'Material is not selected.')


    def EditTab_ReplaceImageFromFile(self):
        try:
            item = self.MaterialIconListView.selectedItems()[0].text()
            category_index = self.ui.treeWidget.selectedIndexes()[0]
            category_name = self.ui.treeWidget.itemFromIndex(category_index).text(0)
            image_path,image_type = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Image', filter=filetype)
            
            if os.path.isfile(image_path):
                destination = os.path.join(self.CategoryPath, category_name, item, displayImg_folderName)
                icon_path = os.path.join(self.CategoryPath, category_name, item)
                source_path = os.path.abspath(image_path)
                from_file = 1
                replc = 1
                _mayaImgPrcs = ImageProcess(from_file, item, destination, icon_path, image_extension, replc, source_path)
                time.sleep(0.1)
                self.LargeImageDisplay()
                self.GenerateMaterialList()

        except IndexError:
            QtWidgets.QMessageBox.about(self, 'Index Error', 'Material is not selected.')


    def EditTab_ReplaceImageFromRenderView(self):
        try:
            item = self.MaterialIconListView.selectedItems()[0].text()
            category_index = self.ui.treeWidget.selectedIndexes()[0]
            category_name = self.ui.treeWidget.itemFromIndex(category_index).text(0)
            destination = os.path.join(self.CategoryPath, category_name, item, displayImg_folderName)
            icon_path = os.path.join(self.CategoryPath, category_name, item)
            source_path = None
            replc = 1
            from_file = -1

            if not os.path.isdir(destination):
                QtWidgets.QMessageBox.about(self, 'Directory Error', 'Create the material first')
            else:
                _mayaImgPrcs = ImageProcess(from_file, item, destination, icon_path, image_extension, replc, source_path)
                time.sleep(0.1)
                self.LargeImageDisplay()
                self.GenerateMaterialList()
                
        except IndexError:
            QtWidgets.QMessageBox.about(self, 'Index Error', 'Material is not selected.')


    def EditTab_ReplaceDescription(self):
        try:
            item = self.MaterialIconListView.selectedItems()[0].text()
            new_text = self.ui.lineEdit.text()
            category_index = self.ui.treeWidget.selectedIndexes()[0]
            category_name = self.ui.treeWidget.itemFromIndex(category_index).text(0)
            destination = os.path.join(self.CategoryPath, category_name, item, item + material_extension)
            with open(destination, "r") as f:
                file_data = json.load(f)
            file_data["description"] = new_text
            open(destination, "w").write(json.dumps(file_data, indent=4))
            self.ui.lineEdit.setText("")
            self.ui.desc_out.setText(new_text)

        except IndexError:
            QtWidgets.QMessageBox.about(self, 'Index Error', 'Material is not selected.')


    def EditTab_RemoveImage(self):
        if self.submit_counter > 0:
            item = self.MaterialIconListView.selectedItems()[0].text()
            category_index = self.ui.treeWidget.selectedIndexes()[0]
            category_name = self.ui.treeWidget.itemFromIndex(category_index).text(0)

            image_data = []
            root = os.path.join(self.CategoryPath, category_name, item, displayImg_folderName)
            for file in os.listdir(root):
                file_path = os.path.join(root,file)
                image_data.append(file_path)

            #put target_path at the begining
            target_path = os.path.join(root, item + image_extension)
            image_data.insert(0, image_data.pop(image_data.index(target_path)))

            os.remove(image_data[self.submit_counter])
            self.LargeImageDisplay()
        else:
            QtWidgets.QMessageBox.about(self, 'Index Error', 'Cannot delete the primary display image.')


    def PasswordCheck(self):
        data = {}
        destination = os.path.join(self.current_path, app, 'options.json')
        if os.path.isfile(destination):
            with open(destination, 'r') as f:
                data = json.load(f)
        else:
            data['pass_use'] = 'False'

        return data


    def ImportMaterial(self):
        if not self.MaterialIconListView.selectedItems():
            QtWidgets.QMessageBox.about(self, 'Error', 'Material is not selected.')
        else:
            item = self.MaterialIconListView.selectedItems()[0].text()
            category_index = self.ui.treeWidget.selectedIndexes()[0]
            category_name = self.ui.treeWidget.itemFromIndex(category_index).text(0)
            destination = os.path.join(self.CategoryPath, category_name, item)
            _mayaRead = ReadFiles(item, destination, material_extension)


    def CreateRepository(self):
        text, ok = QtWidgets.QInputDialog.getText(self, 'Admin', 'Password:')
        if text == self.password and ok:
            repository_file = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Directory', options=QtWidgets.QFileDialog.ShowDirsOnly))
            if not repository_file:
                return
            else:
                run = 1
                for f in os.listdir(repository_file):
                    if f == 'MatLib_Repository':
                        run = 0
                        break

                if run == 1:
                    self.catdialog = QtWidgets.QDialog(self)
                    create_mainlayout = QtWidgets.QVBoxLayout()
                    create_layout = QtWidgets.QFormLayout()
                    rep_label = QtWidgets.QLabel('Display Name:')
                    rep_label_result = QtWidgets.QLineEdit()
                    rep_pwdcheck = QtWidgets.QCheckBox('Password Protection')
                    rep_pwd = QtWidgets.QLabel('Password:')
                    rep_pwd_result = QtWidgets.QLineEdit()
                    rep_pwd_result.setEchoMode(QtWidgets.QLineEdit.Password)

                    rep_pwd_result.setEnabled(rep_pwdcheck.checkState() == QtCore.Qt.Checked)
                    rep_pwdcheck.stateChanged.connect(lambda state : rep_pwd_result.setEnabled(state==QtCore.Qt.Checked))

                    create_layout.addRow(rep_label, rep_label_result)
                    create_layout.addRow(rep_pwdcheck)
                    create_layout.addRow(rep_pwd, rep_pwd_result)
                    create_buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, self.catdialog)
                    create_mainlayout.addLayout(create_layout)
                    create_mainlayout.addWidget(create_buttons)
                    self.catdialog.setLayout(create_mainlayout)
                    self.catdialog.setWindowTitle('Create Repository Dialog')

                    create_buttons.accepted.connect(lambda : self.CreateRepositoryFiles(file_path=repository_file, label=rep_label_result.text(), check=rep_pwdcheck.checkState(), pwd=rep_pwd_result.text()))
                    create_buttons.rejected.connect(self.catdialog.reject)

                    self.catdialog.show()

                else:
                    QtWidgets.QMessageBox.about(self, 'Error', '{} already exists in this directory.'.format(rep_name))

        if text != self.password and ok:
            QtWidgets.QMessageBox.about(self, 'Admin', 'Wrong Password')


    def CreateRepositoryFiles(self, file_path, label, check, pwd):
        if len(label) == 0:
            QtWidgets.QMessageBox.about(self, 'Error', 'Display Name must have atleast 1 character')
        elif check == QtCore.Qt.Checked and len(pwd) == 0:
            QtWidgets.QMessageBox.about(self, 'Error', 'Password must be at least 1 character long.')
        else:
            for renderer in supported_renderers:
                root = '{}/{}/{}/{}'.format(rep_name, app, renderer, category_folderName)
                path = os.path.join(file_path,root)
                if not os.path.exists(path):
                    os.makedirs(path)
            pwd_bytes = pwd.encode('utf-8')
            pswd = base64.b64encode(pwd_bytes)
            pswd_check = 'False'
            if check == QtCore.Qt.Checked:
                pswd_check = 'True'

            data = {'password' : pswd.decode('utf-8'),
                    'pass_use' : pswd_check,
                    'label' : label}

            file_dir = "{}/{}/options.json".format(rep_name, app)
            open(os.path.abspath(os.path.join(file_path, file_dir)), "w").write(json.dumps(data, indent=4))

            self.catdialog.close()


    def DeleteRepository(self):
        repo_count = self.ui.comboBox.count()
        if repo_count == 1:
            QtWidgets.QMessageBox.about(self, 'Error', 'This action cannot be done.\nExpects aditional repositories.')
        else:
            text, ok = QtWidgets.QInputDialog.getText(self, 'Admin', 'Password:')
            if text == self.password and ok:
                if self.ui.comboBox.count() > 1:
                    del_dialog = QtWidgets.QDialog()
                    del_dialog.setWindowTitle('Delete Repository')
                    del_dialog.setWindowIcon(QtGui.QIcon(os.path.join(ui_icon_path, 'MatlibLogoNS_small.svg')))
                    item_box = QtWidgets.QComboBox()

                    item_box.setStyleSheet("""
                                            QMenuBar::item::selected {
                                                background-color : %s;
                                            }
                                            QMenu::item::selected {
                                                background-color : %s;
                                            }
                                            QComboBox QAbstractItemView {
                                                selection-background-color : %s;
                                            }
                                            QListView::item:selected {
                                                selection-background-color : %s;
                                            }
                                            """ %(_color.__selectedbackground__, _color.__selectedbackground__, _color.__selectedbackground__, _color.__selectedbackground__))


                    for i in range(repo_count):
                        repo_item = self.ui.comboBox.itemText(i)
                        if repo_item != "Default Repository":
                            item_box.addItem(repo_item)

                    layout = QtWidgets.QFormLayout(del_dialog)
                    layout.addRow('Delete Repository:', item_box)
                    button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, del_dialog)
                    layout.addWidget(button_box)

                    button_box.accepted.connect(del_dialog.accept)
                    button_box.rejected.connect(del_dialog.reject)

                    ok = del_dialog.exec_()
                    if ok == QtWidgets.QDialog.Accepted:
                        file_path = None
                        del_index = item_box.currentIndex()
                        del_item = item_box.itemText(del_index)

                        with open(config_path, "r+") as f:
                            file_data = json.load(f)
                            for renderer in supported_renderers:
                                for idx,file in enumerate(file_data[app][renderer]["repository"]):
                                    if file == del_item:
                                        file_path = file_data[app][renderer]["dirs"][idx]
                                        file_data[app][renderer]["dirs"].pop(idx)
                                        file_data[app][renderer]["current_index"] = 0
                                        file_data[app][renderer]["repository"].pop(idx)

                                        current_index = idx

                        open(config_path, "w").write(json.dumps(file_data, indent=4))
                        if os.path.isdir(file_path):
                            shutil.rmtree(file_path, ignore_errors=False, onerror=None)

                        self.ui.comboBox.setCurrentIndex(0)
                        self.ui.comboBox.removeItem(current_index)
                        self.UpdateRepository(0)

            if text != self.password and ok:
                QtWidgets.QMessageBox.about(self, 'Admin', 'Wrong Password')


    def UpdateRepository(self, index):
        with open(config_path, "r+") as f:
            file_data = json.load(f)
            file_data[app][self.renderer]["current_index"] = index
            f.seek(0)
            json.dump(file_data, f, indent=4)

        index = file_data[app][self.renderer]["current_index"]
        path = file_data[app][self.renderer]["dirs"][index]

        self.current_path = path
        self.CategoryPath = os.path.join(path, app, self.renderer, category_folderName)
        self.ui.treeWidget.clear()
        self.GenerateCategories()
        self.MaterialIconListView.clear()
        self.CategoryStyleChange()


    def LinkRepository(self):
        repository_file= QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Repository')
        subfolders = []
        check_folder = "MatLib_Repository"
        check = 0
        lbl = ''
        repository_path = None
        if repository_file:
            for renderer in supported_renderers:
                count = 0
                compare_list = [app, renderer, category_folderName]
                for root,dirs,files in os.walk(os.path.abspath(repository_file)):
                    for d in dirs:
                        if d in compare_list:
                            compare_list.remove(d)
                            count += 1
                        if d == check_folder:
                            repository_path = os.path.join(root,d)
                    if os.path.basename(root) == check_folder:
                        repository_path = root

                options_path = os.path.abspath(os.path.join(repository_path, app, 'options.json'))
                #check existing repositories
                found = -1
                with open(config_path, "r") as f:
                    file_data = json.load(f)
                for file in file_data.values():
                    for f in file[renderer]["dirs"]:
                        if repository_path == f:
                            found = 1
                            break

                if found == 1:
                    QtWidgets.QMessageBox.about(self, 'Error', 'Selected Repository is already in the repository list.')
                    break

                else:
                    if count == 3:
                        if repository_file:
                            check = 1
                            data = {}
                            with open(options_path , 'r') as f:
                                data = json.load(f)

                            with open(config_path, "r+") as f:
                                file_data = json.load(f)
                                file_data[app][renderer]["dirs"].append(repository_path)
                                file_data[app][renderer]["repository"].append(data['label'])
                                f.seek(0)
                                json.dump(file_data, f, indent=4)
                                lbl = data['label']

                    else:
                        QtWidgets.QMessageBox.about(self, 'Error', 'Selected folder is not eligible.')
                        break

            if check == 1:
                self.ui.comboBox.addItem(lbl)




    def UnLinkRepository(self):
        repo_count = self.ui.comboBox.count()
        if repo_count == 1:
            QtWidgets.QMessageBox.about(self, 'Error', 'This action cannot be done.\nThere are no aditional repositories to unlink.')

        elif repo_count > 1:
            unlink_dialog = QtWidgets.QDialog()
            unlink_dialog.setWindowTitle('Unlink Repository')
            unlink_dialog.setWindowIcon(QtGui.QIcon(os.path.join(ui_icon_path, 'MatlibLogoNS_small.svg')))
            item_box = QtWidgets.QComboBox()

            item_box.setStyleSheet("""
                        QMenuBar::item::selected {
                            background-color : %s;
                        }
                        QMenu::item::selected {
                            background-color : %s;
                        }
                        QComboBox QAbstractItemView {
                            selection-background-color : %s;
                        }
                        QListView::item:selected {
                            selection-background-color : %s;
                        }
                        """ %(_color.__selectedbackground__, _color.__selectedbackground__, _color.__selectedbackground__, _color.__selectedbackground__))


            for i in range(repo_count):
                repo_item = self.ui.comboBox.itemText(i)
                if repo_item != "Default Repository":
                    item_box.addItem(repo_item)

            layout = QtWidgets.QFormLayout(unlink_dialog)
            layout.addRow('Unlink Repository:', item_box)
            button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, unlink_dialog)
            layout.addWidget(button_box)

            button_box.accepted.connect(unlink_dialog.accept)
            button_box.rejected.connect(unlink_dialog.reject)

            ok = unlink_dialog.exec_()
            if ok == QtWidgets.QDialog.Accepted:
                unlink_index = item_box.currentIndex()
                unlink_item = item_box.itemText(unlink_index)

                with open(config_path, "r+") as f:
                    file_data = json.load(f)
                    for renderer in supported_renderers:
                        file_path = None
                        for idx,file in enumerate(file_data[app][renderer]["repository"]):
                            if file == unlink_item:
                                file_path = file_data[app][renderer]["dirs"][idx]
                                file_data[app][renderer]["dirs"].pop(idx)
                                file_data[app][renderer]["current_index"] = 0
                                file_data[app][renderer]["repository"].pop(idx)

                                current_index = idx

                open(config_path, "w").write(json.dumps(file_data, indent=4))

                self.ui.comboBox.setCurrentIndex(0)
                self.ui.comboBox.removeItem(current_index)
                self.UpdateRepository(0)


    def on_transferclick(self):
        self.dialog.from_repository.clear()
        self.dialog.to_repository.clear()
        for i in range(self.ui.comboBox.count()):
            repo_item = self.ui.comboBox.itemText(i)
            self.dialog.from_repository.addItem(repo_item)
            self.dialog.to_repository.addItem(repo_item)

        self.dialog.show()


    def on_editclick(self):
        self.matdisplay.show()



#win = MainWindow()
#win.show()
