import bpy
from .bp_lib import bp_types, bp_unit, bp_utils
from . import room_utils

class Room_PT_library_settings(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Library"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 18

    def draw(self, context):
        layout = self.layout
        props = room_utils.get_room_scene_props(context)
        props.draw(layout)


class Room_OT_wall_prompts(bpy.types.Operator):
    bl_idname = "room.wall_prompts"
    bl_label = "Wall Prompts"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager           
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.prop(self.assembly.obj_x,'location',index=0,text="Width")
        col.prop(self.assembly.obj_y,'location',index=1,text="Depth")
        col.prop(self.assembly.obj_z,'location',index=2,text="Height")


class Room_OT_room_prompts(bpy.types.Operator):
    bl_idname = "room.room_prompts"
    bl_label = "Room Prompts"

    assembly = None

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        room_bp = room_utils.get_room_bp(context.object)
        self.assembly = bp_types.Assembly(room_bp)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout

        wall_thickness = self.assembly.get_prompt("Wall Thickness")

        col = layout.column(align=True)
        col.prop(self.assembly.obj_x,'location',index=0,text="Width")
        col.prop(self.assembly.obj_y,'location',index=1,text="Depth")
        col.prop(self.assembly.obj_z,'location',index=2,text="Height")

        col = layout.column(align=True)
        col.prop(self.assembly.obj_bp,'location',index=0,text="Location X")
        col.prop(self.assembly.obj_bp,'location',index=1,text="Location Y")
        col.prop(self.assembly.obj_bp,'location',index=2,text="Location Z")

        wall_thickness.draw(layout)


bpy.utils.register_class(Room_PT_library_settings)
bpy.utils.register_class(Room_OT_wall_prompts)
bpy.utils.register_class(Room_OT_room_prompts)        