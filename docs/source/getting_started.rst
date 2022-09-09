Getting Started
++++

Lets go over the Icons and their functions in the MatLib shelf.

.. image:: /images/shelf_icons.jpg

Material Library
====

Material library, as it is called, is the main window where you create, store and import materials to your scene.



Runing Material Library first time
----

When MatLib runs, if it is used for the first time or if the repository you used before has been deleted, it will allow you to select a folder to create a new repository named as  'Default Repository' and automatically links the repository path to MatLib.

Make sure you select a location that has enough space.

User Interface
----

.. image:: /images/matlib_ui_explain.png

There are 6 sections in the interface:

#. Renderer Selection
#. Repository Selection
#. Categories
#. Materials
#. Content Display
#. MenuBar

Renderer Selection
____

**Renderer Selection**, lists all the render engines that loaded on your DCC application which MatLib can support.

If you have more than one renderer that supported by MatLib.Since the properties of the materials belong to different renderers,switching between them will change the categories and materials

Repository Selection
____

The repository is the area where the files and folders required for MatLib are stored. The selected repository calls and displays the registered categories and materials belonging to these categories.

This is the area where you will choose which repository MatLib will run on.

.. tip:: Additional repositories are usefull for team enviroment for collabration.
         For personal usage, this is not an important subject since most likely you dont need to create additional repositories.
         

When you link a new repository, it is added to this menu with the given name.

When a repository other than Default Repository is selected, it will appear in a slightly reddish color as a reminder.


Categories
____

Categories are areas where materials are stored. For example, materials such as chrome, copper and aluminum fall into the category of metals.Basicly it is a list of material types based on which renderer is selected.

By changing the renderer or changing the repository,Category section will be updated accordingly.


**Create a Category**

To create a category, you must give the category a name (such as metals) on the dialog screen that opens after pressing the ``+`` button under the category section.
Pressing the accept button will immediately add the new category to the Categories menu.

**Delete a Category**

To delete a category, you need to type **'YES'** in capital letters in the dialog box that opens after pressing the ``-`` button.

Since some repositories are protected with a password, the password screen will appear after pressing the ``-`` button. If the correct password is entered, a dialog will pop up asking if you are sure, same as unencrypted repositories.

.. warning::
   Deleted repositories do not have backup files, so the deletion cannot be undone.


Materials
____

This is the area where the materials in the selected category are displayed.

The buttons in the lower left corner are used to add or remove materials from the selected category.

**Add a Material**

To add material, first make sure that the render engine is set to the same as the render selection.

After choosing the right render engine, enter the desired aspect ratio in the render settings. This ratio is important for the size of the icon to be used for the material.

Assign the material to an object of your choice.

Render the material with Maya’s native renderview.

.. warning::
   Do not try to render with render engine's own frame buffer, Not all of the render engines have Python support for frame buffer.

When the rendering is completed, select the Shading Group (SG) node of the material from *Hypershade* or *NodeEditor* and click the ``Add Material to Category`` button in MatLib. Pressing this button will open up a new dialog box and ask you to fill in the material name and description.

.. image:: /images/ShadingGroup.jpg

.. tip::
   In Maya, all materials come with a shading group attached to it.It holds information such as the lights that illuminate the material, the object that uses this        material, and what kind of material has been added to it.
   
   More info: https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2016/ENU/Maya/files/GUID-AFA1881C-B5F4-4514-ADC6-A166CA25558D-htm.html


**The material name** is the label of the material that will be included in the material icon. This is also important for the search bar. 

**The description** is, where you can put some notes about the material.

It is possible to change the description later on from the edit tab.It does not have to be filled.

**Delete a Material**

After selecting the material to be deleted from the MatLib window, click the ``Delete Material from Category`` button at the bottom left. As with deleting a category, typing **'YES'** in capital letters at a dialog asking if you are sure, will delete this material.

If the repository is protected by a password, you must first enter the password correctly in the window that appears.

.. warning::
   Deleted materials do not have backup files, so the deletion cannot be undone.
   
**Import Material**

As the naming suggests, this will import the material information and generate the materials into the current scene. After the material is created you will just need to assign the material to an object.

**Search Bar**

Search bar will hide all the other materials which do not have all the characters in their material name from the selected category.

Content Display
____

MenuBar
____
