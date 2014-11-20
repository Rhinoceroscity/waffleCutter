from pymel.core import windows, modeling, general

#Projects grids of cuts onto polygon objects
class waffleCutter():
    def __init__(self):
        #Init the GUI
        self.waffleCutterGUI()
    
    #Gets the current, or last, camera from the last selected modeling panel
    def getCurrentCamera(self):
        panel = windows.getPanel(wf = True)
        print("Panel: " + panel)
        if panel!='':
            print("PanelType: " + windows.getPanel(to = panel))
            if ("modelPanel" == windows.getPanel(to = panel)):
                if "|" in panel:
                    panel = panel.split("|")[-1]
                camera = windows.modelEditor(panel, q = True, cam = True)
                print("Camera: " + camera)
                nodeType = general.nodeType(camera)
                print("NodeType Camera: " + nodeType)
                
                if (nodeType=="transform"):
                    return camera
                    #c = general.listRelatives(camera, c = True)
                    #if general.nodeType(c[0])=="camera":
                        #return c[0]
                elif (nodeType=="camera"):
                    c = general.listRelatives(p = True)
                    return c[0]
                else:
                    return ''
                    print("No camera found")
            else:
                return ''
                print("Last panel was not a modeling panel")
        else:
            return ''
            print("No panel found with focus")
    
    #def lockToCamera(self):
    
    def alignToCamera(self):
        if general.objExists("WaffleSliceGizmo"):
            cam = self.getCurrentCamera()
            if cam!='' and general.objExists(cam):
                general.xform("WaffleSliceGizmo", t=[general.getAttr(cam+".translateX"),
                                                     general.getAttr(cam+".translateY"),
                                                     general.getAttr(cam+".translateZ"),]
                                                , ro = [general.getAttr(cam+".rotateX"),
                                                     general.getAttr(cam+".rotateY"),
                                                     general.getAttr(cam+".rotateZ"),]
                                                ,ws = True)
                general.rotate("WaffleSliceGizmo", [0,90,0], os = True, r = True)
    
    def createGizmo(self):
        ##All this needs to do is create a control square comprised of one transform and a bunch of shape objects parented to it.
        #First check to see if a gizmo exists that maybe got messed up or something.  Delete that and recreate it
        if general.objExists("WaffleSliceGizmo"):
            general.delete("WaffleSliceGizmo")
        
        general.group(n = "WaffleSliceGizmo", em = True)
        
        _deleteArray = []
        _shapesArray = []
        _c = []
        _c.append(modeling.nurbsSquare(n = "gizmoSquare1", nr = [0,0,1] ,c = [0, 0, 0], sl1 = 50, sl2 = 100))
        _c.append(modeling.nurbsSquare(n = "gizmoSquare2", nr = [0,1,0] ,c = [0, 0, 0], sl1 = 100, sl2 = 50))
        
        [general.parent(child, "WaffleSliceGizmo", r = True) for child in _c]
        for child in general.listRelatives("WaffleSliceGizmo", ad = True):
            if general.objectType(child)=="nurbsCurve":
                general.parent(child, "WaffleSliceGizmo", r = True, s = True)
        else:
            [general.delete(child) for child in general.listRelatives("WaffleSliceGizmo", type = "transform")]
        #WaffleSliceGizmo is the group that is created.  Iterate through it, find a useable transform, get all the shapes, and assign
        #All the shapes to a transform
        general.delete("WaffleSliceGizmo", ch = True)
        general.select("WaffleSliceGizmo")

    def deleteGizmo(self):
        if general.objExists("WaffleSliceGizmo"):
            general.delete("WaffleSliceGizmo")
    
    def performSlice(self):
        #Make sure theres a gizmo, otherwise theres no point in doing anything
        if general.objExists("WaffleSliceGizmo"):
            #Get the step size and step count from the appropriate sliders
            step_size = windows.floatSliderGrp("stepSizeSlider", q = True, v = True)
            step_count = int(windows.floatSliderGrp("stepCountSlider", q = True, v = True))
            #Get the axes filter from the radio buttons
            axes = windows.radioButtonGrp("axesRadioButtonGrp", q = True, sl = True)
            #Iterate through the selected objects and create an array of sliceable ones
            sliceArray = []
            for child in general.ls(sl = True):
                if (child!="WaffleSliceGizmo"):
                    #Make sure the selection is either a transform or mesh
                    if (general.objectType(child)=="transform" or general.objectType(child)=="mesh"):
                        sliceArray.append(child)
            else:
                #If anything was added to the array, then move forwards with the waffle slice
                if len(sliceArray)>0:
                    #Create the slicing proxies that will push the proper transforms and rotates into the slice arguments
                    general.group(n = "slice_proxy_x", em = True)
                    general.xform("slice_proxy_x", t=[general.getAttr("WaffleSliceGizmo.translateX"),
                                                 general.getAttr("WaffleSliceGizmo.translateY"),
                                                 general.getAttr("WaffleSliceGizmo.translateZ"),]
                                                 , ro = [general.getAttr("WaffleSliceGizmo.rotateX"),
                                                 general.getAttr("WaffleSliceGizmo.rotateY"),
                                                 general.getAttr("WaffleSliceGizmo.rotateZ"),]
                                                 ,ws = True)
                    general.group(n = "slice_proxy_y", em = True)
                    general.xform("slice_proxy_y", t=[general.getAttr("WaffleSliceGizmo.translateX"),
                                                 general.getAttr("WaffleSliceGizmo.translateY"),
                                                 general.getAttr("WaffleSliceGizmo.translateZ"),]
                                                 , ro = [general.getAttr("WaffleSliceGizmo.rotateX"),
                                                 general.getAttr("WaffleSliceGizmo.rotateY"),
                                                 general.getAttr("WaffleSliceGizmo.rotateZ"),]
                                                 ,ws = True)
                    general.rotate("slice_proxy_y", (90, 0, 0), r = True, os = True)
                    general.parent("slice_proxy_x", "WaffleSliceGizmo")
                    general.parent("slice_proxy_y", "WaffleSliceGizmo")
                    #Iterate through the list of objects
                    for child in sliceArray:
                        #Move the slicers by half of the total distance they're going to need to slice through
                        general.move("slice_proxy_x", [0,0,(-1*((step_size*step_count)/2))] , r = True, ls = True)#, z = True)
                        general.move("slice_proxy_y", [0, (-1*((step_size*step_count)/2)),0], r = True, ls = True)#, y = True)
                        #Get the options for x, y, or both
                        #Do the slices, and for each iteration, bump each proxy forwards by their allotted amount
                        for i in range(step_count):
                            if (axes == 1 or axes == 3):
                                general.move("slice_proxy_x", [0, 0, step_size] , r = True, ls = True)#, z = True)
                                pos = general.xform("slice_proxy_x", ws = True, q = True, t = True)
                                rot = general.xform("slice_proxy_x", ws = True, q = True, ro = True)
                                modeling.polyCut(child, ro = rot , pc = pos)
                                general.delete(child, ch = True)
                                
                            if (axes == 2 or axes == 3):
                                general.move("slice_proxy_y", [0, step_size, 0], r = True, ls = True)#, y = True)
                                pos = general.xform("slice_proxy_y", ws = True, q = True, t = True)
                                rot = general.xform("slice_proxy_y", ws = True, q = True, ro = True)
                                modeling.polyCut(child, ro = rot , pc = pos)
                                general.delete(child, ch = True)
                        else:
                            #Reset the position of the proxies after each object so they dont fly off into the distance
                            general.xform("slice_proxy_x", t=[general.getAttr("WaffleSliceGizmo.translateX"),
                                                         general.getAttr("WaffleSliceGizmo.translateY"),
                                                         general.getAttr("WaffleSliceGizmo.translateZ"),]
                                                         , ws = True)
                            general.xform("slice_proxy_y", t=[general.getAttr("WaffleSliceGizmo.translateX"),
                                                         general.getAttr("WaffleSliceGizmo.translateY"),
                                                         general.getAttr("WaffleSliceGizmo.translateZ"),]
                                                         , ws = True)
                            
                    else:
                        #Clean up the slice proxies
                        general.delete("slice_proxy_x")
                        general.delete("slice_proxy_y")
        else:
            print("No slice gizmo")
    
    def waffleCutterGUI(self):
        ##Check if the window exists, if it does, delete it, otherwise / afterwards, create it
        if windows.window("waffleCutterWindow", exists=True):
            windows.deleteUI("waffleCutterWindow")
        windows.window("waffleCutterWindow", t = "Waffle Cutter", sizeable = False, w = 300, h = 200)
        
        windows.columnLayout() #Overall column layout
        ##MORE COLUMN LAYOUT CONTROLS HERE
        ##

        windows.frameLayout("waffleCutterGizmos", l = "Waffle Cutter Gizmo", w = 300)
        windows.rowLayout(nc = 3)
        windows.iconTextButton("createGizmoButton", style = "iconAndTextVertical", l = "Create Gizmo", image1 = "menuIconModify.png", c = lambda: self.createGizmo())
        windows.iconTextButton("deleteGizmoButton", style = "iconAndTextVertical", l = "Delete Gizmo", image1 = "menuIconModify.png", c = lambda: self.deleteGizmo())
        windows.iconTextButton("alignGizmoButton", style = "iconAndTextVertical", l = "Align to Camera", image1 = "menuIconModify.png", c = lambda: self.alignToCamera())
        windows.setParent(u = True)
        windows.setParent(u = True)
        #windows.separator(h = 10, w = 300, style = "in")
        
        windows.frameLayout("waffleCutterSettings", l = "Waffle Cutter Settings", w = 300)
        windows.columnLayout()
        windows.floatSliderGrp("stepSizeSlider", l = "Step Size", field = True, cw3 = (80, 30, 150), min = 0.1, max = 100, v = 5)
        windows.floatSliderGrp("stepCountSlider", l = "Step Count", field = True, cw3 = (80, 30, 150), min = 5, max = 200, v = 100, pre = 0)
        windows.radioButtonGrp("axesRadioButtonGrp", nrb = 3, l = "Axes", labelArray3 = ["X", "Y", "Both"], cw4 = [80,50,50,50], sl = 3)
        windows.setParent(u = True)
        windows.setParent(u = True)
        ##MORE COLUMN LAYOUT CONTROLS HERE
        ##

        windows.button("waffleSliceButton", l = "Waffle Slice", h = 50, w = 300, c = lambda event: self.performSlice())
        windows.setParent(u = True)
                #Show the window
        windows.showWindow("waffleCutterWindow")

waffleCutter()
