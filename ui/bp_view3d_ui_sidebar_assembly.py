import bpy
from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        UIList,
        )
from ..bp_lib import bp_unit, bp_utils, bp_types

class VIEW3D_PT_assembly(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Assembly"
    bl_category = "Builder"
    bl_options = {'DEFAULT_CLOSED'}
    
    def get_assembly_collection(self,obj):
        if obj:
            for coll in obj.users_collection:
                if "IS_ASSEMBLY" in coll:
                    return coll
        return None

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='',icon='STICKY_UVS_LOC')

    def get_selection_icon(self,obj,context):
        if context.view_layer.objects.active.name == obj.name:
            return 'RESTRICT_SELECT_OFF'
        elif obj.select_get():
            return 'DECORATE'
        else:
            return 'BLANK1'

    def draw(self, context):
        layout = self.layout
        layout.operator('bp_assembly.create_new_assembly',icon='ADD')
        active_coll = self.get_assembly_collection(context.object)

        if active_coll:
            assembly = bp_types.Assembly(active_coll)
            col = layout.column(align=True)
            box = col.box()
            row = box.row(align=True)
            row.prop(active_coll.bp_props,'assembly_tabs',expand=True)
            box = col.box()
            if active_coll.bp_props.assembly_tabs == 'MAIN':
                box.prop(active_coll,'name')
                col = box.column(align=True)
                col.label(text="Dimensions:")
                col.prop(assembly.obj_x,'location',index=0,text="X")
                col.prop(assembly.obj_y,'location',index=1,text="Y")
                col.prop(assembly.obj_z,'location',index=2,text="Z")

                col = box.column()
                s_col = col.split()
                s_col.prop(assembly.obj_bp,'location')
                s_col.prop(assembly.obj_bp,'rotation_euler',text="Rotation")

            if active_coll.bp_props.assembly_tabs == 'PROMPTS':
                assembly.obj_prompts.prompt_page.draw_prompts(box,'OBJECT')

            if active_coll.bp_props.assembly_tabs == 'OBJECTS':
                box.operator('bp_assembly.add_object',icon='ADD')
                # row = box.row(align=True)
                # row.operator('bp_object.select_object',text="BP",icon=self.get_selection_icon(assembly.obj_bp,context)).obj_name = assembly.obj_bp.name
                # row.operator('bp_object.select_object',text="X",icon=self.get_selection_icon(assembly.obj_x,context)).obj_name = assembly.obj_x.name
                # row.operator('bp_object.select_object',text="Y",icon=self.get_selection_icon(assembly.obj_y,context)).obj_name = assembly.obj_y.name
                # row.operator('bp_object.select_object',text="Z",icon=self.get_selection_icon(assembly.obj_z,context)).obj_name = assembly.obj_z.name
                obj_col = box.column(align=True)
                mesh_box = obj_col.box()
                mesh_box.label(text="Mesh Objects")
                mesh_col = mesh_box.column(align=True)

                empty_box = obj_col.box()
                empty_box.label(text="Empty Objects")         
                empty_col = empty_box.column(align=True)

                curve_box = obj_col.box()
                curve_box.label(text="Curve Objects")
                curve_col = curve_box.column(align=True)

                for obj in active_coll.objects:
                    skip_names = {assembly.obj_bp.name,assembly.obj_x.name,assembly.obj_y.name,assembly.obj_z.name,assembly.obj_prompts.name}
                    if obj.name not in skip_names:
                        if obj.type == 'MESH':
                            row = mesh_col.row(align=True)
                        if obj.type == 'EMPTY':
                            row = empty_col.row(align=True)
                        if obj.type == 'CURVE':
                            row = curve_col.row(align=True)

                        row.operator('bp_object.select_object',text=obj.name,icon=self.get_selection_icon(obj,context)).obj_name = obj.name

            if active_coll.bp_props.assembly_tabs == 'LOGIC':
                pass
            
class VIEW3D_PT_assembly_library(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Assembly Library"
    bl_category = "Builder"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='',icon='STICKY_UVS_LOC')

    def draw(self, context):
        layout = self.layout
        wm_props = context.window_manager.bp_lib
        for item in wm_props.library_items:
            props = layout.operator('library.draw_library_item',text=item.name)
            props.package_name = item.package_name
            props.module_name = item.module_name
            props.class_name = item.class_name

classes = (
    VIEW3D_PT_assembly,
    VIEW3D_PT_assembly_library,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()        