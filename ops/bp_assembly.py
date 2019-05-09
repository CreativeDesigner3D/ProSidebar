import bpy
from bpy.types import (
        Operator,
        Panel,
        UIList,
        PropertyGroup,
        AddonPreferences,
        )
from bpy.props import (
        StringProperty,
        BoolProperty,
        IntProperty,
        CollectionProperty,
        BoolVectorProperty,
        PointerProperty,
        FloatProperty,
        )
import os
from ..bp_lib import bp_types

class ASSEMBLY_OT_create_new_assembly(Operator):
    bl_idname = "bp_assembly.create_new_assembly"
    bl_label = "Create New Assembly"
    bl_description = "This will create a new assembly"
    bl_options = {'UNDO'}

    assembly_name: StringProperty(name="Assembly Name",default="New Assembly")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        assembly = bp_types.Assembly()
        assembly.create_assembly()
        assembly.obj_x.location.x = 1
        assembly.obj_y.location.y = 1
        assembly.obj_z.location.z = 1
        assembly.obj_bp.select_set(True)
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Enter the name of the assembly to add.")
        layout.prop(self,'assembly_name')

class ASSEMBLY_OT_add_object(Operator):
    bl_idname = "bp_assembly.add_object"
    bl_label = "Add Object to Assembly"
    bl_description = "This will add a new object to the assembly"
    bl_options = {'UNDO'}

    assembly_name: StringProperty(name="Assembly Name",default="New Assembly")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        assembly = bp_types.Assembly(context.view_layer.active_layer_collection.collection)
        assembly.add_empty("New Empty")
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Enter the name of the assembly to add.")
        layout.prop(self,'assembly_name')

classes = (
    ASSEMBLY_OT_create_new_assembly,
    ASSEMBLY_OT_add_object
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()