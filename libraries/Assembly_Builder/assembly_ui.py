import bpy
from .bp_lib import bp_types, bp_unit, bp_utils

class Assembly_PT_library_settings(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Library"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 18

    def draw(self, context):
        layout = self.layout
        props = room_utils.get_room_scene_props(context)
        props.draw(layout)


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

        col = layout.column(align=True)
        col.prop(self.assembly.obj_x,'location',index=0,text="X Dimension")
        col.prop(self.assembly.obj_y,'location',index=1,text="Y Dimension")
        col.prop(self.assembly.obj_z,'location',index=2,text="Z Dimension")

        col = layout.column(align=True)
        col.prop(self.assembly.obj_bp,'rotation_euler',index=2,text="Z Rotation")


bpy.utils.register_class(Assembly_PT_library_settings)
bpy.utils.register_class(Assembly_OT_assembly_prompts)