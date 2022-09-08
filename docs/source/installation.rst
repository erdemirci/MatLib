Installation
****
Information below will guide you through the installation of MatLib.

Downloading MatLib
____
Visit https://www.erdemirci3d.com/matlib to download the latest version of MatLib.

System Requirement
====

Current version of MatLib supports:

* Microsoft Windows
* Autodesk Maya
* Python 2 and 3

============  ==========  ========  ===============   ========
Application     Version   Renderer  Frame Buffer      OS
============  ==========  ========  ===============   ========
Maya          2018-2023   Redshift  Maya RenderView   Windows
Maya          2018-2023   Arnold    Maya RenderView   Windows
Maya          2018-2023   Vray      Maya RenderView   Windows
============  ==========  ========  ===============   ========

.. warning::
   If you are planing to use MatLib with multiple users, make sure all of the users have the same version of the renderer.


Installing on Windows
____

Download MatLib and run the executable.In some cases, Windows displays a warning due to the unknown source.You can ignore this warning by clicking on "More Info" and then on the "Run anyway" button.

.. image:: /images/windows_warning_page1.jpg

.. image:: /images/windows_warning_page2.jpg

After skipping the welcome and license agreement pages, there is a target DCC Applications page where you can choose one or more applications that you can install MatLib.

.. image:: /images/matlib_installer_page3.jpg

.. warning::
   If you are unable to select any of the applications which means either you dont have the right version of the DCC application or the default path location of the Maya.env is changed manually.If that is the case, follow the manual installation instruction.

Choose the location for MatLib files will be installed.

.. image:: /images/matlib_installer_page4.jpg

After the installation is completed, run Maya and you will be able to see the MatLib shelf.

.. image:: /images/matlib_shelfonMaya.jpg

Manual Installation
====
Unlike using the installer, there are some steps to make MatLib work.

#. Go to github and download the latest version of MatLib.

After the download is completed, extract Matlib to the desired install directory.

Create folder inside C:/Users/{user_name}/AppData/Local and name it MatLib.

Copy the files inside the {install directory}/MatLib/files/ folder and paste all of them in to C:/Users/{user_name}/AppData/Local/MatLib folder.

Copy modules folder from MatLib install directory and paste it to C:/Users/{user_name}/Documents/maya/{maya_version}/ .If you already have a modules folder in there, just copy and paste the MatLib.mod file from {install directory}/Matlib/Modules.

.. tip::
   For some reason if your Maya enviroment path is different than the default, change the path of the MatLib.mod accordingly!

Edit MatLib.mod file by using Notepad and change the first PATH to {install directory}/MatLib and the second one with {install directory}/MatLib/scripts .


