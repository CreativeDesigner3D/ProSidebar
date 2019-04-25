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
import math      


class VIEW3D_PT_materials(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Materials"
    bl_category = "Materials"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        obj = context.object
        scene = context.scene
        layout = self.layout    

        row = layout.row(align=True)
        row.scale_y = 1.3
        row.operator("library.add_material_from_library",text="Material Library",icon='DISK_DRIVE')
        row.menu('LIBRARY_MT_material_library',text="",icon="DISCLOSURE_TRI_DOWN")

        if len(bpy.data.materials) > 0:
            layout.template_list("BP_UL_materials", "", bpy.data, "materials", scene.bp_props, "selected_material_index", rows=4)
            
            # layout.template_list("MATERIAL_UL_matslots", "", bpy.data, "materials", scene.bp_props, "selected_material_index", rows=4)
            mat = bpy.data.materials[scene.bp_props.selected_material_index]
            layout.prop(mat,'name')
        layout.operator('library.assign_material',text="Assign Selected Material",icon='NONE')

class BP_UL_materials(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name,icon_value=icon)
        layout.operator('bp_material.delete_material',icon='X',text="",emboss=False).material_name = item.name         

class VIEW3D_MT_add_material(bpy.types.Menu):
    bl_label = "Add Material"

    def draw(self, context):
        layout = self.layout
        layout.operator("material.new",icon='ZOOMIN')
        layout.operator("material.create_principled_material",icon='SMOOTH')
        layout.operator("material.create_material_from_image",icon='IMAGE_COL')               


classes = (
    VIEW3D_PT_materials,
    BP_UL_materials,
    VIEW3D_MT_add_material
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()        