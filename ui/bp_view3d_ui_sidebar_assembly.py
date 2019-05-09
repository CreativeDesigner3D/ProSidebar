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
    bl_category = "Object"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text='',icon='BLANK1')

    def draw(self, context):
        layout = self.layout
        layout.operator('bp_assembly.create_new_assembly')
        obj = context.object
        active_coll = None

        if obj:
            for coll in obj.users_collection:
                if "IS_ASSEMBLY" in coll:
                    active_coll = coll

        if active_coll:
            assembly = bp_types.Assembly(active_coll)
            col = layout.column(align=True)
            box = col.box()
            row = box.row(align=True)
            row.prop(active_coll.bp_props,'assembly_tabs',expand=True)
            box = col.box()
            if active_coll.bp_props.assembly_tabs == 'MAIN':
                box.label(text=active_coll.name)
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
                box.operator('bp_assembly.add_object')
                for obj in active_coll.objects:
                    box.label(text=obj.name)

            if active_coll.bp_props.assembly_tabs == 'LOGIC':
                pass
            

classes = (
    VIEW3D_PT_assembly,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()        