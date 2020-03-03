import bpy
import os
import math
from .bp_lib import bp_types, bp_unit, bp_utils
from . import room_utils
from . import data_walls
from . import data_doors

class ROOM_OT_draw_molding(bpy.types.Operator):
    bl_idname = "room.draw_molding"
    bl_label = "Draw Molding"

    def execute(self, context):
        pass

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

    class_name = ""

    def execute(self, context):
        self.starting_point = ()
        self.get_class_name()
        self.create_drawing_plane(context)
        self.create_wall()
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def get_class_name(self):
        name, ext = os.path.splitext(os.path.basename(self.filepath))
        self.class_name = name

    def create_wall(self):
        props = room_utils.get_room_scene_props(bpy.context)
        wall = eval("data_walls." + self.class_name + "()")
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
        #THIS IS NEEDED TO SET THE ANGLE OF THE NEXT WALL WHEN ROTATING
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

    def set_placed_properties(self,obj):
        if obj.type == 'MESH':
            obj.display_type = 'TEXTURED'          
        for child in obj.children:
            self.set_placed_properties(child) 

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
            self.set_placed_properties(self.current_wall.obj_bp)
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
        if self.previous_wall:
            prev_right_angle = self.previous_wall.get_prompt("Right Angle") 
            prev_right_angle.set_value(0)

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

    starting_point = ()

    def execute(self, context):
        self.starting_point = ()
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

    def position_object(self,selected_point,selected_obj):
        if self.starting_point == ():
            self.assembly.obj_bp.location = selected_point
        else:
            x = selected_point[0] - self.starting_point[0]
            y = selected_point[1] - self.starting_point[1]

            self.assembly.obj_x.location.x = math.fabs(x)
            self.assembly.obj_y.location.y = math.fabs(y)

    def modal(self, context, event):
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        selected_point, selected_obj = bp_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        self.position_object(selected_point,selected_obj)

        if self.event_is_place_object(event):
            if self.starting_point == ():
                self.starting_point = (selected_point[0],selected_point[1],selected_point[2])
            else:
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


class ROOM_OT_place_door(bpy.types.Operator):
    bl_idname = "room.place_door"
    bl_label = "Place Door"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")
    
    drawing_plane = None

    door = None
    obj = None
    exclude_objects = []

    class_name = ""

    def execute(self, context):
        self.get_class_name()
        self.create_drawing_plane(context)
        self.create_door()
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def get_class_name(self):
        name, ext = os.path.splitext(os.path.basename(self.filepath))
        self.class_name = name

    def create_door(self):
        props = room_utils.get_room_scene_props(bpy.context)
        self.door = eval("data_doors." + self.class_name + "()")
        self.door.draw_door()
        self.set_child_properties(self.door.obj_bp)

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

    def set_placed_properties(self,obj):
        if obj.type == 'MESH':
            obj.display_type = 'TEXTURED'          
        for child in obj.children:
            self.set_placed_properties(child) 

    def create_drawing_plane(self,context):
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.display_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)

    def get_boolean_obj(self,obj):
        if 'IS_BOOLEAN' in obj and obj['IS_BOOLEAN'] == True:
            return obj
        for child in obj.children:
            return self.get_boolean_obj(child)

    def add_boolean_modifier(self,wall_mesh):
        obj_bool = self.get_boolean_obj(self.door.obj_bp)
        if wall_mesh:
            mod = wall_mesh.modifiers.new(obj_bool.name,'BOOLEAN')
            mod.object = obj_bool
            mod.operation = 'DIFFERENCE'

    def parent_door_to_wall(self,obj_wall_bp):
        x_loc = bp_utils.calc_distance((self.door.obj_bp.location.x,self.door.obj_bp.location.y,0),
                                       (obj_wall_bp.matrix_local[0][3],obj_wall_bp.matrix_local[1][3],0))
        self.door.obj_bp.location = (0,0,0)
        self.door.obj_bp.rotation_euler = (0,0,0)
        self.door.obj_bp.parent = obj_wall_bp
        self.door.obj_bp.location.x = x_loc        

    def modal(self, context, event):
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        selected_point, selected_obj = bp_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        self.position_object(selected_point,selected_obj)

        if self.event_is_place_first_point(event):
            self.add_boolean_modifier(selected_obj)
            if selected_obj.parent:
                self.parent_door_to_wall(selected_obj.parent)
            self.create_door()
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
        if selected_obj:
            wall_bp = selected_obj.parent
            if self.door.obj_bp and wall_bp:
                self.door.obj_bp.rotation_euler.z = wall_bp.rotation_euler.z
                self.door.obj_bp.location.x = selected_point[0]
                self.door.obj_bp.location.y = selected_point[1]
                self.door.obj_bp.location.z = 0

    def cancel_drop(self,context):
        obj_list = []
        obj_list.append(self.drawing_plane)
        obj_list.append(self.door.obj_bp)
        for child in self.door.obj_bp.children:
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


bpy.utils.register_class(ROOM_OT_draw_molding)
bpy.utils.register_class(ROOM_OT_draw_multiple_walls)
bpy.utils.register_class(ROOM_OT_place_square_room)
bpy.utils.register_class(ROOM_OT_place_door)