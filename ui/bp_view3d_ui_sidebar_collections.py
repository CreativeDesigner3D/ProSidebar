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
        )
from .. import sidebar_utils

class VIEW3D_PT_collection_info(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Collection"
    bl_category = "Collection"
    bl_options = {'HIDE_HEADER'}
    
    def draw_collection(self,layout,collection,indent_amount):
        row = layout.row()
        row.alignment = 'LEFT'
        if bpy.context.view_layer.active_layer_collection.name == collection.name:
            icon='CHECKBOX_HLT'
            emboss = True
        else:
            emboss = False
            # icon= 'CHECKBOX_DEHLT'
            icon='BLANK1'

        for i in range(0,indent_amount):
            row.label(text="",icon='BLANK1')

        if len(collection.children) > 0:
            row.prop(collection.bp_props,'is_expanded',text="",icon='TRIA_DOWN' if collection.bp_props.is_expanded else 'TRIA_RIGHT',emboss=False)
        else:
            row.label(text="",icon='BLANK1')

        row.prop(collection,'hide_viewport',text="",emboss=False,icon='HIDE_OFF' if collection.hide_viewport else 'HIDE_OFF')
        row.operator('bp_collection.set_active_collection',text=collection.name,emboss=emboss).collection_name = collection.name
        row.operator('bp_collection.delete_collection',text="",icon='X',emboss = False).collection_name = collection.name
        if collection.bp_props.is_expanded:
            for child in collection.children:
                self.draw_collection(layout,child,indent_amount + 1)

    def draw(self, context):
        layout = self.layout
        view_layer = context.view_layer
        master_collection = context.view_layer.layer_collection.collection

        layout.menu('VIEW3D_MT_bp_create_collection',text="Create Collection",icon="DISCLOSURE_TRI_DOWN")

        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        row.label(text="Collection Hierarchy",icon='OUTLINER')
        row.operator('bp_collection.set_active_collection_based_on_selection',icon='ARROW_LEFTRIGHT',text="")
        box = col.box()
        col = box.column(align=True)
        
        self.draw_collection(col,master_collection,0)
        active_collection = view_layer.active_layer_collection.collection

        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        row.label(text="Active Collection",icon='GROUP')
        row.prop(active_collection,'name',text="")
        row.operator('object.move_to_collection',icon='EXPORT',text="")

        col.template_list("COLLECTION_UL_objects", "", active_collection, "objects", active_collection.bp_props, "selected_object_index", rows=4)  


class VIEW3D_PT_collections_panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Collections Visibility"
    bl_category = "Collection"
    bl_ui_units_x = 10

    def _draw_collection(self, layout, view_layer, collection, index):
        need_separator = index
        for child in collection.children:
            index += 1

            if child.exclude:
                continue

            if child.collection.hide_viewport:
                continue

            if need_separator:
                layout.separator()
                need_separator = False

            icon = 'BLANK1'
            has_objects = True
            if child.has_selected_objects(view_layer):
                icon = 'LAYER_ACTIVE'
            elif child.has_objects():
                icon = 'LAYER_USED'
            else:
                has_objects = False

            has_visible_objects = has_objects and child.has_visible_objects(view_layer)

            row = layout.row()
            sub = row.split(factor=0.98)
            subrow = sub.row()
            subrow.alignment = 'LEFT'
            subrow.active = has_visible_objects
            subrow.operator("object.hide_collection", text=child.name, icon=icon, emboss=False).collection_index = index

            sub = row.split()
            subrow = sub.row(align=True)
            subrow.alignment = 'RIGHT'
            icon = 'HIDE_OFF' if has_visible_objects else 'HIDE_ON'
            props = subrow.operator("object.hide_collection", text="", icon=icon, emboss=False)
            props.collection_index = index
            props.toggle = True
            subrow.prop(child.collection, "hide_select", text="", emboss=False)

        for child in collection.children:
            index = self._draw_collection(layout, view_layer, child, index)

        return index

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False

        layout.label(text="Collections Visibility")

        view_layer = context.view_layer
        # We pass index 0 here beause the index is increased
        # so the first real index is 1
        # And we start with index as 1 because we skip the master collection
        self._draw_collection(layout, view_layer, view_layer.layer_collection, 0)

class COLLECTION_UL_objects(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        sel_icon = 'RADIOBUT_OFF'
        if item in context.selected_objects:
            sel_icon = 'DOT'
        if item == context.view_layer.objects.active:
            sel_icon = 'RADIOBUT_ON'
        layout.label(text="",icon=sel_icon)
        layout.label(text=item.name,icon=sidebar_utils.get_object_icon(item))
        
        layout.prop(item,'hide_viewport',emboss=False,icon_only=True)
        layout.prop(item,'hide_select',emboss=False,icon_only=True)
        layout.prop(item,'hide_render',emboss=False,icon_only=True)

class VIEW3D_MT_bp_create_collection(bpy.types.Menu):
    bl_label = "Create Collection"

    def draw(self, context):
        layout = self.layout
        layout.operator('bp_collection.create_empty_collection')
        layout.operator('bp_collection.create_collection_from_selected_objects')

classes = (
    VIEW3D_PT_collection_info,
    # VIEW3D_PT_collections_panel,
    COLLECTION_UL_objects,
    VIEW3D_MT_bp_create_collection,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
