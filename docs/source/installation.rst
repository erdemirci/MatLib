Installation
****

Downloading MatLib
____
Visit https://www.erdemirci3d.com/matlib to download the latest version of MatLib.

System Requirement
====

Current version of MatLib only supports:

* Microsoft Windows
* Autodesk Maya


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
~~~~

Download MatLib and run the executable.In some cases, Windows displays a warning due to the unknown source.You can ignore this warning by clicking on "More Info" and then on the "Run anyway" button.

.. image:: /images/windows_warning_page1.jpg

.. image:: /images/windows_warning_page2.jpg

After skipping the welcome and license agreement pages, there is a target DCC Applications page where you can choose one or more applications that you can install MatLib.

.. image:: /images/matlib_installer_page3.jpg

.. warning::
   If you are unable to select any of the applications which means either you dont have the right version of the DCC application or the default location for the env is    changed manually.If that is the case, follow the manuel installation instruction.

Choose the location for MatLib files will be installed.

.. image:: /images/matlib_installer_page4.jpg



Manual Installation
====

Go to github and download the latest version of MatLib.
After the installation completed, extract Matlib to the desired install directory.
Copy the files inside the MatLib folder.
Create folder inside C:/Users/{user_name}/AppData/Local and name it MatLib.
Paste all the files to this folder.
Copy modules folder from 


