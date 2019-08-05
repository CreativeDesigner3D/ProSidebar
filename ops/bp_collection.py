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

    def select_children_objects(self,collection):
        for obj in collection.collection.objects:
            obj.select_set(True)       
        for child in collection.children:
            self.select_children_objects(child) 

    def search_children(self,collection):
        for child in collection.children:
            if child.collection.name == self.collection_name:
                bpy.ops.object.select_all(action = 'DESELECT')
                bpy.context.view_layer.active_layer_collection = child
                self.select_children_objects(child)
            else:
                self.search_children(child)

    def execute(self, context):
        self.search_children(context.view_layer.layer_collection)
        if self.collection_name == context.view_layer.layer_collection.collection.name:
            context.view_layer.active_layer_collection = context.view_layer.layer_collection
        return {'FINISHED'}

class COLLECTION_OT_create_empty_collection(Operator):
    bl_idname = "bp_collection.create_empty_collection"
    bl_label = "Create Empty Collection"
    bl_description = "This will create an empty collection and add it to the active scenes view_layer"
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

class COLLECTION_OT_create_collection_from_selected_objects(Operator):
    bl_idname = "bp_collection.create_collection_from_selected_objects"
    bl_label = "Create Collection From Selected Objects"
    bl_description = "This will create a collection and add the selected objects to it"
    bl_options = {'UNDO'}

    collection_name: StringProperty(name="Collection Name",default="New Collection")
    add_base_point: BoolProperty(name="Add Base Point",default=False)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        layer_collection = context.view_layer.active_layer_collection
        coll = bpy.data.collections.new(self.collection_name)
        layer_collection.collection.children.link(coll)
        bpy.ops.bp_collection.set_active_collection(collection_name=coll.name)
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Enter the name of the collection to add.")
        layout.prop(self,'collection_name')
        layout.prop(self,'add_base_point')


class COLLECTION_OT_delete_collection(Operator):
    bl_idname = "bp_collection.delete_collection"
    bl_label = "Delete Collection"
    bl_description = "This will delete the collection"
    bl_options = {'UNDO'}

    collection_name: StringProperty(name="Collection Name",default="New Collection")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.collection_name != 'Master Collection':
            coll = bpy.data.collections[self.collection_name]
            bpy.data.collections.remove(coll)
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        if self.collection_name == 'Master Collection':
            layout.label(text="You cannot remove the Master Collection",icon='ERROR')
        else:
            layout.label(text="Are you sure you want to remove the collection?")
            layout.label(text="Colleciton Name: " + self.collection_name)


class COLLECTION_OT_set_active_collection_based_on_selection(Operator):
    bl_idname = "bp_collection.set_active_collection_based_on_selection"
    bl_label = "Set Active Collection Based on Selection"
    bl_description = "This sets the active collection based on the active selection"
    bl_options = {'UNDO'}

    collection_name: StringProperty(name="Collection Name",default="New Collection")

    def execute(self, context):
        obj = context.object
        for col in obj.users_collection:
            bpy.ops.bp_collection.set_active_collection(collection_name=col.name)
            break
        return {'FINISHED'}

classes = (
    COLLECTION_OT_create_empty_collection,
    COLLECTION_OT_create_collection_from_selected_objects,
    COLLECTION_OT_set_active_collection,
    COLLECTION_OT_delete_collection,
    COLLECTION_OT_set_active_collection_based_on_selection
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()        