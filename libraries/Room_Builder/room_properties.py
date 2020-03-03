import bpy
from .bp_lib import bp_types, bp_unit, bp_utils


class RoomLibrary_PT_library_settings(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Library"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 18

    def draw(self, context):
        layout = self.layout
        layout.label(text="Room Library Settings")


class ROOM_OT_part_prompts(bpy.types.Operator):
    bl_idname = "room.part_prompts"
    bl_label = "Part Prompts"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager           
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Part Prompts")


class ROOM_OT_wall_prompts(bpy.types.Operator):
    bl_idname = "room.wall_prompts"
    bl_label = "Wall Prompts"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager           
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Wall Prompts")


class ROOM_OT_room_prompts(bpy.types.Operator):
    bl_idname = "room.room_prompts"
    bl_label = "Room Prompts"

    coll = None
    assembly = None

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        #TODO: How do I get the room collection
        for coll in context.object.users_collection:
            if "IS_ROOM" in coll:
                self.coll = coll
                break
        self.assembly = bp_types.Assembly(self.coll)
        wm = context.window_manager           
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.label(text=self.assembly.coll.name)

        col = layout.column(align=True)
        col.prop(self.assembly.obj_bp,'location',index=0,text="Location X")
        col.prop(self.assembly.obj_bp,'location',index=1,text="Location Y")
        col.prop(self.assembly.obj_bp,'location',index=2,text="Location Z")

        col = layout.column(align=True)
        col.prop(self.assembly.obj_x,'location',index=0,text="Width")
        col.prop(self.assembly.obj_y,'location',index=1,text="Depth")
        col.prop(self.assembly.obj_z,'location',index=2,text="Height")

bpy.utils.register_class(RoomLibrary_PT_library_settings)
bpy.utils.register_class(ROOM_OT_part_prompts)
bpy.utils.register_class(ROOM_OT_wall_prompts)
bpy.utils.register_class(ROOM_OT_room_prompts)