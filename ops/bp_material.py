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
from ..bp_lib import bp_unit

class bp_material_OT_delete_material(Operator):
    bl_idname = "bp_material.delete_material"
    bl_label = "Delete Material"
    bl_description = "This will delete the material"
    bl_options = {'UNDO'}

    material_name: StringProperty(name="Material Name")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.material_name in bpy.data.materials:
            mat = bpy.data.materials[self.material_name]
            bpy.data.materials.remove(mat,do_unlink=True)
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Are you sure you want to delete the material?")  
        layout.label(text="Material Name: " + self.material_name)

classes = (
    bp_material_OT_delete_material,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()               