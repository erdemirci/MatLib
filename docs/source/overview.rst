Overview
****

.. image:: /images/MatLib_logo.png
   :scale: 25 %
   :align: center
   
   
Introduction
====


MatLib is a free tool that stores materials for reuse.

Without having to deal with manual work, MatLib organizes the materials that you created and brings them to your scene in a few steps. It also stores the textures in relevant folders automatically.


Software and System Requirements
====

Current version of MatLib supports:

* Microsoft Windows
* Autodesk Maya
* Python 2 and 3

============  ==========  ========  ===============   ========
Application     Version   Renderer  Frame Buffer      OS
============  ==========  ========  ===============   ========
Maya          2019-2023   Redshift  Maya RenderView   Windows
Maya          2019-2023   Arnold    Maya RenderView   Windows
Maya          2019-2023   Vray      Maya RenderView   Windows
============  ==========  ========  ===============   ========

.. warning::
   If you are planing to use MatLib with multiple users, make sure all of the users have the same version of the render engine.


Release notes
====

MatLib beta v0.9
----

* Support for Python 3
* Support for Redshift, Vray and Arnold.
* Create multiple repositories.
* Password protection for category and material deletion.
* Transfer materials between repositories.
* Adding multiple display images for materials.
* Material attribute display.

MatLib beta v0.9.2
----

* Bug fix for UDIM types.
* Bug fix for shading engine's renderer parameters.
* Bug fix for face selection assignment for material.
* "Transfer to project" now creates 'sourceimages' folder if it does not exist.


