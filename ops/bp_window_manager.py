import bpy
import os
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
from ..bp_utils import utils_library

#TODO: Setup this to work with pro sidebar library drop operators

class WM_OT_drag_and_drop(bpy.types.Operator):
    bl_idname = "wm.drag_and_drop"
    bl_label = "Drag and Drop"
    bl_description = "This is a special operator that will be called when an image is dropped from the file browser"

    filepath: bpy.props.StringProperty(name="Message",default="Error")

    def execute(self, context):
        props = utils_library.get_scene_props()
        if props.library_tabs == 'SCRIPT':
            pass        
        if props.library_tabs == 'OBJECT':
            bpy.ops.library.drop_object_from_library(filepath=self.filepath)
        if props.library_tabs == 'COLLECTION':
            bpy.ops.library.drop_collection_from_library(filepath=self.filepath)
        if props.library_tabs == 'MATERIAL':
            bpy.ops.library.drop_material_from_library(filepath=self.filepath)
        if props.library_tabs == 'WORLD':
            bpy.ops.library.drop_world_from_library(filepath=self.filepath)        
        return {'FINISHED'}

classes = (
    WM_OT_drag_and_drop,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
