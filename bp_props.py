import bpy
from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        UIList,
        )
from bpy.props import (
        BoolProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        CollectionProperty,
        EnumProperty,
        )
import os

def update_object_selection(self,context):
    if self.selected_object_index < len(context.scene.objects):
        bpy.ops.object.select_all(action = 'DESELECT')
        obj = context.scene.objects[self.selected_object_index]
        obj.select_set(True)
        context.view_layer.objects.active = obj

def update_object_selection_from_collection(self,context):
    if self.selected_object_index < len(context.view_layer.active_layer_collection.collection.objects):
        bpy.ops.object.select_all(action = 'DESELECT')
        obj = context.view_layer.active_layer_collection.collection.objects[self.selected_object_index]
        obj.select_set(True)
        context.view_layer.objects.active = obj

def update_world_selection(self,context):
    if self.selected_world_index <= len(bpy.data.worlds) - 1:
        world = bpy.data.worlds[self.selected_world_index]
        context.scene.world = world

class BP_Scene_Props(PropertyGroup):
    selected_object_index: IntProperty(name="Selected Object Index", default=0, update = update_object_selection)
    selected_world_index: IntProperty(name="Selected World Index", default=0, update = update_world_selection)
    selected_material_index: IntProperty(name="Selected Material Index", default=0)

    @classmethod
    def register(cls):
        bpy.types.Scene.bp_props = PointerProperty(
            name="BP Props",
            description="ProSidebar Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.bp_props


class BP_Collection_Props(PropertyGroup):
    is_expanded: BoolProperty(name="Is Expanded", default=False)
    selected_object_index: IntProperty(name="Select Object Index", default=False,update = update_object_selection_from_collection)

    @classmethod
    def register(cls):
        bpy.types.Collection.bp_props = PointerProperty(name="BP Props",description="Blender Pro Props",type=cls)
        
    @classmethod
    def unregister(cls):
        del bpy.types.Collection.bp_props

classes = (
    BP_Scene_Props,
    BP_Collection_Props,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
