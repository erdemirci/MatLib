Installation
****
Information below will guide you through the installation of MatLib.

Downloading MatLib
____
Visit https://www.erdemirci3d.com/?page_id=298 to download the latest version of MatLib.

Installing on Windows
____

Download MatLib and run the executable. In some cases, Windows displays a warning due to the unknown source. You can ignore this warning by clicking on "More Info" and then on the "Run anyway" button.

.. image:: /images/windows_warning_page1.jpg

.. image:: /images/windows_warning_page2.jpg

After skipping the "Welcome" and "License Agreement" pages, there is a "Target DCC Applications" page where you can choose one or more applications that you can install MatLib for.

.. image:: /images/matlib_installer_page3.jpg

.. warning::
   If you are unable to select any of the applications either you do not have the right version of the DCC application or the default path location of the Maya.env is changed manually. If that is the case, follow the manual installation instruction.

Choose the location for MatLib files to be installed.

.. image:: /images/matlib_installer_page4.jpg

After the installation is complete, run Maya and you will be able to see the MatLib shelf.

.. image:: /images/matlib_shelfonMaya.jpg

Manual Installation
====
Follow the instructions below to make MatLib work with Maya.

* Go to `github <https://github.com/erdemirci/MatLib.git>`_ and download the latest version of MatLib.

* After the download is complete, extract MatLib to the desired install directory.

* Create folder inside C:/Users/{user_name}/AppData/Local and name it MatLib.

.. tip::
   If you cannot see the AppData folder, it means that it is invisible. Go to Control Panel / Appearance and Personalization. Under the File Explorer Options, toggle          "Show hidden files, folders, and drivers" and hit apply.

* Copy the files inside the {install directory}/MatLib/files/ folder and paste all of them in to C:/Users/{user name}/AppData/Local/MatLib folder.

* Copy modules folder from MatLib install directory and paste it to C:/Users/{user name}/Documents/maya/{maya_version}/ .If you already have a modules folder in       there, just copy and paste the MatLib.mod file from {install directory}/Matlib/Modules.

.. tip::
   For some reason if your Maya enviroment path is different than the default, change the path of the MatLib.mod accordingly!

* Edit MatLib.mod file by using Notepad and change the first PATH to {install directory}/MatLib and the second line with {install directory}/MatLib/scripts .




