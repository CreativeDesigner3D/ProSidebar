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

class COLLECTION_OT_set_active_collection(Operator):
    bl_idname = "bp_collection.set_active_collection"
    bl_label = "Set Active Collection"
    bl_description = "This set the active collection"
    bl_options = {'UNDO'}

    collection_name: StringProperty(name="Collection Name",default="New Collection")

    def search_children(self,collection):
        for child in collection.children:
            if child.collection.name == self.collection_name:
                bpy.context.view_layer.active_layer_collection = child
            else:
                self.search_children(child)

    def execute(self, context):
        if self.collection_name == context.view_layer.layer_collection.collection.name:
            context.view_layer.active_layer_collection = context.view_layer.layer_collection
        else:
            self.search_children(context.view_layer.layer_collection)
        return {'FINISHED'}

class COLLECTION_OT_create_collection(Operator):
    bl_idname = "bp_collection.create_collection"
    bl_label = "Create Collection"
    bl_description = "This will create a collection and add it to the active scenes view_layer"
    bl_options = {'UNDO'}

    collection_name: StringProperty(name="Collection Name",default="New Collection")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        layer_collection = context.view_layer.active_layer_collection
        coll = bpy.data.collections.new(self.collection_name)
        layer_collection.collection.children.link(coll)
        bpy.ops.bp_collection.set_active_collection(collection_name=coll.name)
        # for c in layer_collection.collection.children:
        #     if c.name == coll.name:
        #         pass #HOW DO I SET THE ACTIVE COLLECTION
        #         context.view_layer.active_layer_collection = c
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Enter the name of the collection to add.")
        layout.prop(self,'collection_name')


classes = (
    COLLECTION_OT_create_collection,
    COLLECTION_OT_set_active_collection
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()        