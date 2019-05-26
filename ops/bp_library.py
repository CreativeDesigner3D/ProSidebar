import bpy
import os
import inspect
from bpy.types import Operator

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       BoolVectorProperty,
                       PointerProperty,
                       CollectionProperty,
                       EnumProperty)

class LIBRARY_OT_open_browser_window(bpy.types.Operator):
    bl_idname = "library.open_browser_window"
    bl_label = "Open Browser Window"
    bl_description = "This will open the path that is passed in a file browser"

    path: bpy.props.StringProperty(name="Message",default="Error")

    def execute(self, context):
        import subprocess
        if 'Windows' in str(bpy.app.build_platform):
            subprocess.Popen(r'explorer ' + self.path)
        elif 'Darwin' in str(bpy.app.build_platform):
            subprocess.Popen(['open' , os.path.normpath(self.path)])
        else:
            subprocess.Popen(['xdg-open' , os.path.normpath(self.path)])
        return {'FINISHED'}


class LIBRARY_OT_create_new_folder(bpy.types.Operator):
    bl_idname = "library.create_new_folder"
    bl_label = "Create New Folder"
    
    path: bpy.props.StringProperty(name="Path",description="Path to Add Folder to To")
    folder_name: bpy.props.StringProperty(name="Folder Name",description="Folder Name to Create")

    def check(self, context):
        return True

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)
        
    def draw(self, context):
        layout = self.layout
        layout.label("Enter the Category Name to Add")
        layout.prop(self,'folder_name',icon='FILE_FOLDER')

    def execute(self, context):
        path = os.path.join(self.path, self.folder_name)
        
        if not os.path.exists(path):
            os.makedirs(path)
            
        return {'FINISHED'}
    

class LIBRARY_OT_draw_library_item(bpy.types.Operator):
    bl_idname = "library.draw_library_item"
    bl_label = "Draw Library Item"
    bl_description = "This will call the draw function of a library item"

    package_name: bpy.props.StringProperty(name="Package Name")
    module_name: bpy.props.StringProperty(name="Module Name")
    class_name: bpy.props.StringProperty(name="Class Name")

    def execute(self, context):
        pkg = __import__(self.package_name)
        import time
        for modname, modobj in inspect.getmembers(pkg):
            if modname == self.module_name:
                for name, obj in inspect.getmembers(modobj):
                    if name == self.class_name:
                        if hasattr(obj,'draw'):
                            start_time = time.time()
                            product = obj()
                            product.draw()
                            print("Draw Time --- %s seconds ---" % (time.time() - start_time))
        return {'FINISHED'}

classes = (
    LIBRARY_OT_open_browser_window,
    LIBRARY_OT_create_new_folder,
    LIBRARY_OT_draw_library_item,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
