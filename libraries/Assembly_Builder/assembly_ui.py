import bpy
from .bp_lib import bp_types, bp_unit, bp_utils
from . import assembly_utils

class Assembly_PT_library_settings(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Library"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 18

    def draw(self, context):
        layout = self.layout
        # props = room_utils.get_room_scene_props(context)
        # props.draw(layout)


class Assembly_OT_assembly_prompts(bpy.types.Operator):
    bl_idname = "assembly.assembly_prompts"
    bl_label = "Assembly Prompts"

    assembly = None

    def execute(self, context):
        return {'FINISHED'}

    def check(self, context):
        return True

    def invoke(self,context,event):
        assembly_bp = assembly_utils.get_assembly_bp(context.object)
        self.assembly = bp_types.Assembly(assembly_bp)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout

        scene_props = assembly_utils.get_scene_assembly_props(context.scene)

        assembly_bp = assembly_utils.get_assembly_bp(context.object)

        if assembly_bp:
            assembly = bp_types.Assembly(assembly_bp)
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

                skip_names = {assembly.obj_bp.name,assembly.obj_x.name,assembly.obj_y.name,assembly.obj_z.name,assembly.obj_prompts.name}

                for child in assembly.obj_bp.children:
                    
                    if child.name not in skip_names:
                        if child.type == 'MESH':
                            row = mesh_col.row(align=True)
                        if child.type == 'EMPTY':
                            row = empty_col.row(align=True)
                        if child.type == 'CURVE':
                            row = curve_col.row(align=True)

                        row.operator('bp_object.select_object',text=child.name,icon=self.get_selection_icon(child,context)).obj_name = child.name

            if scene_props.assembly_tabs == 'LOGIC':
                pass


bpy.utils.register_class(Assembly_PT_library_settings)
bpy.utils.register_class(Assembly_OT_assembly_prompts)