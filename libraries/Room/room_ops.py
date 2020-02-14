import bpy
import os
from .bp_lib import bp_types, bp_unit, bp_utils

class ROOM_OT_place_square_room(bpy.types.Operator):
    bl_idname = "room.place_square_room"
    bl_label = "Place Square Room"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")
    
    drawing_plane = None
    assembly = None
    obj = None
    
    def execute(self, context):
        self.create_drawing_plane(context)
        self.obj = self.get_object(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def get_object(self,context):
        return bpy.data.objects[self.obj_bp_name]

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
        selected_point, selected_obj = bp_utils.get_selection_point(context,event,exclude_objects=[self.obj])

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
        coll = self.obj.users_collection[0]
        for obj in coll.all_objects:
            obj["PROMPT_ID"] = "room.room_prompts"

    def finish(self,context):
        self.set_prompt_id()
        context.window.cursor_set('DEFAULT')
        if self.drawing_plane:
            bp_utils.delete_obj_list([self.drawing_plane])
        bpy.ops.object.select_all(action='DESELECT')
        self.obj.select_set(True)  
        context.view_layer.objects.active = self.obj 
        context.area.tag_redraw()
        return {'FINISHED'}


bpy.utils.register_class(ROOM_OT_place_square_room)