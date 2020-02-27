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

    current_wall = None
    previous_wall = None
    next_wall = None

    def execute(self, context):
        return {'FINISHED'}

    def check(self, context):
        prev_rot = 0
        next_rot = 0
        left_angle = self.current_wall.get_prompt("Left Angle")
        right_angle = self.current_wall.get_prompt("Right Angle")    

        if self.previous_wall:
            prev_left_angle = self.previous_wall.get_prompt("Left Angle")
            prev_right_angle = self.previous_wall.get_prompt("Right Angle") 
            prev_rot = self.previous_wall.obj_bp.rotation_euler.z  

        if self.next_wall:
            next_left_angle = self.next_wall.get_prompt("Left Angle")
            next_rot = self.next_wall.obj_bp.rotation_euler.z  

        rot = self.current_wall.obj_bp.rotation_euler.z

        left_angle.set_value((rot-prev_rot)/2)
        if self.next_wall:
            right_angle.set_value((rot-next_rot)/2)
            next_left_angle.set_value((next_rot-rot)/2)
        prev_right_angle.set_value((prev_rot-rot)/2)

        self.current_wall.obj_prompts.location = self.current_wall.obj_prompts.location
        if self.previous_wall:
            self.previous_wall.obj_prompts.location = self.previous_wall.obj_prompts.location
        if self.next_wall:
            self.next_wall.obj_prompts.location = self.next_wall.obj_prompts.location
        return True

    def get_next_wall(self,context):
        obj_x = self.current_wall.obj_x
        if obj_x and 'WALL_CONSTRAINT_OBJ_ID' in obj_x:
            if obj_x['WALL_CONSTRAINT_OBJ_ID'] in bpy.data.objects:
                obj_bp = bpy.data.objects[obj_x['WALL_CONSTRAINT_OBJ_ID']]
                self.next_wall = bp_types.Assembly(obj_bp)  

    def get_previous_wall(self,context):
        if len(self.current_wall.obj_bp.constraints) > 0:
            obj_bp = self.current_wall.obj_bp.constraints[0].target.parent
            self.previous_wall = bp_types.Assembly(obj_bp)    

    def invoke(self,context,event):
        wall_bp = room_utils.get_wall_bp(context.object)
        self.current_wall = bp_types.Assembly(wall_bp)   
        self.get_previous_wall(context)
        self.get_next_wall(context)
        wm = context.window_manager           
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout

        left_angle = self.current_wall.get_prompt("Left Angle")
        right_angle = self.current_wall.get_prompt("Right Angle")

        col = layout.column(align=True)
        col.prop(self.current_wall.obj_x,'location',index=0,text="Length")
        col.prop(self.current_wall.obj_y,'location',index=1,text="Thickness")
        col.prop(self.current_wall.obj_z,'location',index=2,text="Height")

        col = layout.column(align=True)
        col.prop(self.current_wall.obj_bp,'rotation_euler',index=2,text="Rotation")

        left_angle.draw(layout)
        right_angle.draw(layout)

        # layout.label(text=str(left_angle.get_value()))
        # layout.label(text=str(right_angle.get_value()))


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