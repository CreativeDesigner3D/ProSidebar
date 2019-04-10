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

class bp_object_OT_collapse_all_modifiers(Operator):
    bl_idname = "bp_object.collapse_all_modifiers"
    bl_label = "Collapse All Modifiers"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.object

    def execute(self, context):
        for mod in context.active_object.modifiers:
            mod.show_expanded = False
        return {'FINISHED'}
    
class bp_object_OT_collapse_all_constraints(Operator):
    bl_idname = "bp_object.collapse_all_constraints"
    bl_label = "Collapse All Constraints"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.object

    def execute(self, context):
        for con in context.active_object.constraints:
            con.show_expanded = False
        return {'FINISHED'}

classes = (
    bp_object_OT_collapse_all_modifiers,
    bp_object_OT_collapse_all_constraints,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                