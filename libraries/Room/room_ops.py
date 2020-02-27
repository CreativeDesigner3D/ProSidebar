import bpy
import os
import math
from .bp_lib import bp_types, bp_unit, bp_utils
from . import room_utils
from . import room_library

class ROOM_OT_draw_multiple_walls(bpy.types.Operator):
    bl_idname = "room.draw_multiple_walls"
    bl_label = "Draw Multiple Walls"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")
    
    drawing_plane = None

    current_wall = None
    previous_wall = None

    starting_point = ()

    assembly = None
    obj = None
    exclude_objects = []

    def execute(self, context):
        self.starting_point = ()
        self.create_drawing_plane(context)
        self.create_wall()
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def create_wall(self):
        props = room_utils.get_room_scene_props(bpy.context)
        wall = room_library.Wall_Mesh()
        wall.draw_wall()
        if self.current_wall:
            self.previous_wall = self.current_wall
        self.current_wall = wall
        self.current_wall.obj_x.location.x = 0
        self.current_wall.obj_y.location.y = props.wall_thickness
        self.current_wall.obj_z.location.z = props.wall_height
        self.set_child_properties(self.current_wall.obj_bp)

    def connect_walls(self):
        # self.current_wall.obj_bp.parent = self.previous_wall.obj_x

        constraint_obj = self.previous_wall.obj_x
        constraint = self.current_wall.obj_bp.constraints.new('COPY_LOCATION')
        constraint.target = constraint_obj
        constraint.use_x = True
        constraint.use_y = True
        constraint.use_z = True

        #I NEED A BETTER WAY TO FIND THE CONSTRAINT OBJ FROM THE BP OBJ
        constraint_obj['WALL_CONSTRAINT_OBJ_ID'] = self.current_wall.obj_bp.name

    def set_child_properties(self,obj):
        obj["PROMPT_ID"] = "room.wall_prompts"   
        if obj.type == 'EMPTY':
            obj.hide_viewport = True    
        if obj.type == 'MESH':
            obj.display_type = 'WIRE'            
        if obj.name != self.drawing_plane.name:
            self.exclude_objects.append(obj)    
        for child in obj.children:
            self.set_child_properties(child)

    def set_placed_properties(self):
        for child in self.current_wall.obj_bp.children:
            if child.type == 'MESH':
                child.display_type = 'TEXTURED'

    def create_drawing_plane(self,context):
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.display_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)

    def modal(self, context, event):
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        selected_point, selected_obj = bp_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        self.position_object(selected_point,selected_obj)
        self.set_end_angles()            

        if self.event_is_place_first_point(event):
            self.starting_point = (selected_point[0],selected_point[1],selected_point[2])
            return {'RUNNING_MODAL'}
            
        if self.event_is_place_next_point(event):
            self.set_placed_properties()
            self.create_wall()
            self.connect_walls()
            self.starting_point = (selected_point[0],selected_point[1],selected_point[2])
            return {'RUNNING_MODAL'}

        if self.event_is_cancel_command(event):
            return self.cancel_drop(context)

        if self.event_is_pass_through(event):
            return {'PASS_THROUGH'} 

        return {'RUNNING_MODAL'}

    def event_is_place_next_point(self,event):
        if self.starting_point == ():
            return False
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            return True
        elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS':
            return True
        elif event.type == 'RET' and event.value == 'PRESS':
            return True
        else:
            return False

    def event_is_place_first_point(self,event):
        if self.starting_point != ():
            return False
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            return True
        elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS':
            return True
        elif event.type == 'RET' and event.value == 'PRESS':
            return True
        else:
            return False

    def event_is_cancel_command(self,event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            return True
        else:
            return False
    
    def event_is_pass_through(self,event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return True
        else:
            return False

    def set_end_angles(self):
        if self.previous_wall and self.current_wall:
            print("SETTING ANGLE")
            left_angle = self.current_wall.get_prompt("Left Angle")
            # right_angle = self.current_wall.get_prompt("Right Angle")    

            # prev_left_angle = self.previous_wall.get_prompt("Left Angle")
            prev_right_angle = self.previous_wall.get_prompt("Right Angle") 

            prev_rot = self.previous_wall.obj_bp.rotation_euler.z  
            rot = self.current_wall.obj_bp.rotation_euler.z

            left_angle.set_value((rot-prev_rot)/2)
            prev_right_angle.set_value((prev_rot-rot)/2)

            self.current_wall.obj_prompts.location = self.current_wall.obj_prompts.location
            self.previous_wall.obj_prompts.location = self.previous_wall.obj_prompts.location            
        
    def position_object(self,selected_point,selected_obj):
        if self.starting_point == ():
            self.current_wall.obj_bp.location = selected_point
        else:
            x = selected_point[0] - self.starting_point[0]
            y = selected_point[1] - self.starting_point[1]
            parent_rot = self.current_wall.obj_bp.parent.rotation_euler.z if self.current_wall.obj_bp.parent else 0
            if math.fabs(x) > math.fabs(y):
                if x > 0:
                    self.current_wall.obj_bp.rotation_euler.z = math.radians(0) + parent_rot
                else:
                    self.current_wall.obj_bp.rotation_euler.z = math.radians(180) + parent_rot
                self.current_wall.obj_x.location.x = math.fabs(x)
                
            if math.fabs(y) > math.fabs(x):
                if y > 0:
                    self.current_wall.obj_bp.rotation_euler.z = math.radians(90) + parent_rot
                else:
                    self.current_wall.obj_bp.rotation_euler.z = math.radians(-90) + parent_rot
                self.current_wall.obj_x.location.x = math.fabs(y)

    def cancel_drop(self,context):
        obj_list = []
        obj_list.append(self.drawing_plane)
        obj_list.append(self.current_wall.obj_bp)
        for child in self.current_wall.obj_bp.children:
            obj_list.append(child)
        bp_utils.delete_obj_list(obj_list)
        return {'CANCELLED'}

    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        if self.drawing_plane:
            bp_utils.delete_obj_list([self.drawing_plane])
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        return {'FINISHED'}


class ROOM_OT_place_square_room(bpy.types.Operator):
    bl_idname = "room.place_square_room"
    bl_label = "Place Square Room"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")
    
    drawing_plane = None
    assembly = None
    obj = None
    exclude_objects = []

    def execute(self, context):
        self.create_drawing_plane(context)
        self.obj = self.get_object(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def set_child_properties(self,obj):
        obj["PROMPT_ID"] = "room.room_prompts"   
        if obj.type == 'EMPTY':
            obj.hide_viewport = True    
        if obj.name != self.drawing_plane.name:
            self.exclude_objects.append(obj)    
        for child in obj.children:
            self.set_child_properties(child)

    def get_object(self,context):
        self.exclude_objects = []
        obj = bpy.data.objects[self.obj_bp_name]
        room_bp = room_utils.get_room_bp(obj)
        self.assembly = bp_types.Assembly(room_bp)
        self.assembly.obj_x.location.x = 1
        self.assembly.obj_y.location.y = 1
        self.set_child_properties(self.assembly.obj_bp)
        return self.assembly.obj_bp

    def create_drawing_plane(self,context):
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.display_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)

    def modal(self, context, event):
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        selected_point, selected_obj = bp_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        if event.ctrl:
            if event.mouse_y > event.mouse_prev_y:
                self.obj.rotation_euler.z += .1
            else:
                self.obj.rotation_euler.z -= .1
        else:
            self.position_object(selected_point,selected_obj)

        if self.event_is_place_object(event):
            return self.finish(context)

        if self.event_is_cancel_command(event):
            return self.cancel_drop(context)
        
        if self.event_is_pass_through(event):
            return {'PASS_THROUGH'}        
        
        return {'RUNNING_MODAL'}

    def event_is_place_object(self,event):
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            return True
        elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS':
            return True
        elif event.type == 'RET' and event.value == 'PRESS':
            return True
        else:
            return False

    def event_is_cancel_command(self,event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            return True
        else:
            return False
    
    def event_is_pass_through(self,event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return True
        else:
            return False

    def position_object(self,selected_point,selected_obj):
        self.obj.location = selected_point

    def cancel_drop(self,context):
        obj_list = []
        obj_list.append(self.drawing_plane)
        obj_list.append(self.obj)
        bp_utils.delete_obj_list(obj_list)
        return {'CANCELLED'}
    
    def set_prompt_id(self):
        for child in self.assembly.obj_bp.children:
            child["PROMPT_ID"] = "room.room_prompts"

    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        if self.drawing_plane:
            bp_utils.delete_obj_list([self.drawing_plane])
        bpy.ops.object.select_all(action='DESELECT')
        self.obj.select_set(True)  
        context.view_layer.objects.active = self.obj 
        context.area.tag_redraw()
        return {'FINISHED'}


bpy.utils.register_class(ROOM_OT_draw_multiple_walls)
bpy.utils.register_class(ROOM_OT_place_square_room)