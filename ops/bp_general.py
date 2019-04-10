import bpy
from bpy.types import Header, Menu, Operator, UIList, PropertyGroup
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       BoolVectorProperty,
                       PointerProperty,
                       EnumProperty,
                       CollectionProperty)
import os

class general_OT_open_browser_window(Operator):
    bl_idname = "bp_general.open_browser_window"
    bl_label = "Open Browser Window"
    bl_description = "This will open the path that is passed in a file browser"

    path: StringProperty(name="Message",default="Error")

    def execute(self, context):
        import subprocess
        if 'Windows' in str(bpy.app.build_platform):
            subprocess.Popen(r'explorer ' + self.path)
        elif 'Darwin' in str(bpy.app.build_platform):
            subprocess.Popen(['open' , os.path.normpath(self.path)])
        else:
            subprocess.Popen(['xdg-open' , os.path.normpath(self.path)])
        return {'FINISHED'}

class general_OT_open_new_editor(Operator):
    bl_idname = "bp_general.open_new_editor"
    bl_label = "Open New Editor"

    space_type: StringProperty(name="Space Type")
    
    @classmethod
    def poll(cls, context):
        return True
        
    def execute(self, context):      
        bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        for window in context.window_manager.windows:
            if len(window.screen.areas) == 1 and window.screen.areas[0].type == 'PREFERENCES':
                window.screen.areas[0].type = self.space_type
        return {'FINISHED'}

class general_OT_open_texture_editor(bpy.types.Operator):
    bl_idname = "bp_general.open_texture_editor"
    bl_label = "Open Texture Editor"

    @classmethod
    def poll(cls, context):
        if context.object and context.object.type == 'MESH':
            return True
        else:
            return False
        
    def execute(self, context):
        if context.object.mode == 'OBJECT':
            bpy.ops.object.editmode_toggle()
            
        bpy.ops.mesh.select_all(action='SELECT')
        
        bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        for window in context.window_manager.windows:
            if len(window.screen.areas) == 1 and window.screen.areas[0].type == 'PREFERENCES':
                window.screen.areas[0].type = 'IMAGE_EDITOR'
        return {'FINISHED'} 

classes = (
    general_OT_open_browser_window,
    general_OT_open_new_editor,
    general_OT_open_texture_editor,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()        