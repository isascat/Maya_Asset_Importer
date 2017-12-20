"""
    Maya ToolBox
    
    Copyright (C) 2017 Isabelle Chen
    All Rights Reserved.
    isafx.com
    
    Description:
        A suite of tools for use in Maya.
    
    Dependencies:
        pymel
        viewGui
        
"""


from functools import partial

from AssetImporter.asset_import_tool import *


class AssetImporterWin(object):

    def __init__(self):

        # access to the AssetImporter tool itself
        self.importer = AssetImporter()

        # UI
        self._windowSize    = (1000,600)
        self._iconSize      = (128,128)
        self._windowName    = "AssetImporterWindow"
        self._assetGrid     = ""
        self._importedList  = ""


    def show(self):
        """
        show()
            
            Build the window and show it
            If one already exists, it will be deleted first.
        """

        self.close()
        
        # make the window
        win = cmds.window(self._windowName, 
                            title       = "Asset Import Tool", 
                            sizeable    = True, 
                            retain      = False, 
                            widthHeight = self._windowSize)
        
 
        cmds.columnLayout("c_layout", adj = True)  
        cmds.separator(h=30)
        
        cmds.text("Copyright (c) 2017, Isabelle Chen | isafx.com")   
        
        cmds.separator(h=30)
        
        cmds.text("Loading Functions")
        
        cmds.separator(h=30)
        
        cmds.button("b_zxy", label="Refresh Library", h=30, c=self.refreshAssets, p="c_layout")
        cmds.button("reloadImportedButton", label="Refresh Imported", h=30, c=self.refreshImported, p="c_layout")

        cmds.button("deleteReference", label="Delete Selected Asset", h=30, c=self.deleteAssets, p="c_layout")
        cmds.separator()
        
        cmds.text("",h=20)
        
        cmds.separator()            
        form = cmds.formLayout(numberOfDivisions=100,p="c_layout")

        reloadLibButton = cmds.text("Asset Library")
        scroll = cmds.scrollLayout(width=600, height = 420)

        library = cmds.gridLayout(  cellWidth   = self._iconSize[0]+20, 
                                    cellHeight  = self._iconSize[1]+40, 
                                    nc          = 4 )

        cmds.setParent(form)

        importedButtons = cmds.rowLayout(nc=2)
        reloadImportedButton = cmds.text("Imported Asset List")

        cmds.setParent(form)
        importedList = cmds.textScrollList()

                
        cmds.formLayout(form, e=True, 
                            attachForm=[(reloadLibButton, 'top', 5), (reloadLibButton, 'left', 5),
                                        (scroll, 'left', 5), (scroll, 'bottom', 5),
                                        (importedButtons, 'right', 5), (importedButtons, 'top', 5),
                                        (importedList, 'right', 5), (importedList, 'bottom', 5),
                            ],
                            attachControl=[(scroll, 'top', 5, reloadLibButton),
                                            (importedButtons, 'left', 5, scroll),
                                            (importedList, 'left', 5, scroll), (importedList, 'top', 5, importedButtons)
                            ],
                        )
        
        # set up the commands to run
        cmds.textScrollList(importedList, e=True, selectCommand=self.importedItemSelected)



        # we need to save the names of the UI elements so that they
        # are easy to refer to in other methods.
        self._windowName    = win
        self._assetGrid     = library
        self._importedList  = importedList
        
  
        
        

        cmds.showWindow(win)

    
    def close(self):
        """
        close()
            
            close an existing window
        """

        if cmds.window(self._windowName, q=True, exists=True):
            cmds.deleteUI(self._windowName)
    

    # The reason this callback method uses *args as its parameter
    # list is because Maya will try and pass some values to this method
    # when its attached to a UI object. If it were a checkbox, this could
    # be a True or False value if its checked or not. We just need it 
    # here to catch the values, even if we don't need them.
    def deleteAssets(self, *args):
        asset = cmds.ls(sl=1,l=1)
        a=cmds.referenceQuery(asset,rfn=1)
        cmds.file(removeReference= True, referenceNode = a)
                
        
    def refreshAssets(self, *args):
        """
        refreshAssets(*args)
            
            A callback command that refreshes the list of available
            assets ready for import. 
            The "Refresh Library" button calls this when clicked.
        """
        
        # clear out any previous children of the grid layout
        children = cmds.gridLayout(self._assetGrid, q=True, childArray=True)
        if children:
            for child in children:
                cmds.deleteUI(child)
        
        # the grid layout seems to  have a bug where it wont redraw
        # and show the newly added items until you trigger something
        # that makes it redraw. We can force this by hiding the layout
        # while adding new items, and then show it again after.
        cmds.gridLayout(self._assetGrid, e=True, vis=False) 
        
        for asset in self.importer.list(allShows=True):
            
            # this is an example of a callback using the functools
            # module. Its a way to package up a method and arguments
            # so that maya can call it later, such as by just calling:  cmd()
            # We imported this as:   from functools import partial
            cmd = partial(self.importer.load, asset)

            cmds.iconTextButton(    parent  = self._assetGrid, 
                                    style   = 'iconAndTextVertical', 
                                    width   = self._iconSize[0], 
                                    height  = self._iconSize[1], 
                                    image1  = asset.image, 
                                    label   = '%s \n(%s)' % (asset.name, asset.show),
                                    command = cmd ) 

        
        cmds.gridLayout(self._assetGrid, e=True, vis=True)    

    def refreshImported(self, *args):
        """
        refreshImported(*args)

            A callback command the refreshes the list of already
            imported assets in the scene. 
            The "Refresh Imported" button calls this when clicked.
        """
        
        cmds.textScrollList(self._importedList, e=True, removeAll=True)

        for node, asset in self.importer.findImported():
            cmds.textScrollList(self._importedList, e=True, append=node)
    

    def importedItemSelected(self, *args):
        """
        importedItemSelected(*args)

            A callback command that selects the object in the scene
            when the corresponding item is selected in the list
            of imported assets.
        """

        nodes = cmds.textScrollList(self._importedList, q=True, selectItem=True)
        if nodes:
            node = nodes[0]
            if cmds.objExists(node):
                cmds.select(node, r=True)
        
                               

def show():
    """
    show()
        
        A convenience function for showing the User Interface.
    """
    i = AssetImporterWin()
    i.show()

    return i
