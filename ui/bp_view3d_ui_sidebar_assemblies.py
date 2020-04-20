import bpy
from ..bp_lib import bp_types, bp_utils
from ..bp_utils import utils_library


def draw_assembly_properties(context, layout, assembly):
    scene_props = utils_library.get_scene_props()

    col = layout.column(align=True)
    box = col.box()
    row = box.row(align=True)
    row.prop(scene_props,'assembly_tabs',expand=True)
    box = col.box()
    if scene_props.assembly_tabs == 'MAIN':
        box.prop(assembly.obj_bp,'name')

        col = box.column(align=True)
        col.label(text="Dimensions:")
        col.prop(assembly.obj_x,'location',index=0,text="X")
        col.prop(assembly.obj_y,'location',index=1,text="Y")
        col.prop(assembly.obj_z,'location',index=2,text="Z")

        col = box.column()
        s_col = col.split()
        s_col.prop(assembly.obj_bp,'location')
        s_col.prop(assembly.obj_bp,'rotation_euler',text="Rotation")

    if scene_props.assembly_tabs == 'PROMPTS':
        assembly.obj_prompts.prompt_page.draw_prompts(box)

    if scene_props.assembly_tabs == 'OBJECTS':

        skip_names = {assembly.obj_bp.name,assembly.obj_x.name,assembly.obj_y.name,assembly.obj_z.name,assembly.obj_prompts.name}

        # obj_col = box.column(align=True)
        # obj_box = obj_col.box()

        row = box.row()
        row.label(text="Objects",icon='OUTLINER_OB_MESH')
        row.operator('bp_assembly.add_object',text="Add Object",icon='ADD')

        mesh_col = box.column(align=True)

        for child in assembly.obj_bp.children:
            if child.name not in skip_names:
                row = mesh_col.row(align=True)
                if child == context.object:
                    row.label(text="",icon='RADIOBUT_ON')
                elif child in context.selected_objects:
                    row.label(text="",icon='DECORATE')
                else:
                    row.label(text="",icon='RADIOBUT_OFF')
                row.operator('bp_object.select_object',text=child.name,icon=bp_utils.get_object_icon(child)).obj_name = child.name

        # obj = context.object

        # if obj and obj.parent and obj.parent == assembly.obj_bp and obj.name not in skip_names:
            
        #     box.prop(context.object,'name')

        #     draw_transform(context,box,obj)

        #     if context.object.type not in {'EMPTY','CAMERA','LATTICE','LIGHT','SPEAKER'}:
        #         box.label(text="Materials",icon='MATERIAL')
        #         draw_material_properties(context,box,context.object)

    if scene_props.assembly_tabs == 'LOGIC':
        pass#TODO: IMPLEMENT DRIVER INTERFACE

class VIEW3D_PT_assembly_properties(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Assembly"
    bl_category = "Assembly"    
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        if context.object and bp_utils.get_assembly_bp(context.object):
            return True
        else:
            return False

    def draw(self, context):
        layout = self.layout
        assembly_bp = bp_utils.get_assembly_bp(context.object)
        assembly = bp_types.Assembly(assembly_bp)   
        draw_assembly_properties(context,layout,assembly)     

classes = (
    VIEW3D_PT_assembly_properties,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                