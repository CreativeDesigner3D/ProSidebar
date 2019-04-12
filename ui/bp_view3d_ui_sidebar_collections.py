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
from ..bp_lib import bp_utils

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
            # row.label(text="",icon='FILE_TICK')
        else:
            icon='BLANK1'
            # row.label(text="",icon='BLANK1')

        for i in range(0,indent_amount):
            row.label(text="",icon='BLANK1')
        row.operator('bp_collection.set_active_collection',text=collection.name,emboss=False,icon=icon).collection_name = collection.name
        for child in collection.children:
            self.draw_collection(layout,child,indent_amount + 1)

    def draw(self, context):
        layout = self.layout
        view_layer = context.view_layer
        master_collection = context.view_layer.layer_collection.collection

        row = layout.row(align=True)
        row.scale_y = 1.3
        row.operator("library.add_collection_from_library",text="Collection Library",icon='DISK_DRIVE')
        row.menu('LIBRARY_MT_collection_library',text="",icon="DISCLOSURE_TRI_DOWN")

        layout.operator('bp_collection.create_collection')

        col = layout.column(align=True)
        box = col.box()
        box.label(text="Collection Hierarchy",icon='OUTLINER')
        box = col.box()
        # col = box.column(align=True)
        
        self.draw_collection(box,master_collection,0)
        active_collection = view_layer.active_layer_collection.collection

        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        row.label(text="Active Collection",icon='GROUP')
        row.prop(active_collection,'name',text="")

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
        layout.label(text=item.name,icon=bp_utils.get_object_icon(item))
        layout.prop(item,'hide_viewport',emboss=False,icon_only=True)
        layout.prop(item,'hide_select',emboss=False,icon_only=True)
        layout.prop(item,'hide_render',emboss=False,icon_only=True)

classes = (
    VIEW3D_PT_collection_info,
    # VIEW3D_PT_collections_panel,
    COLLECTION_UL_objects,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
