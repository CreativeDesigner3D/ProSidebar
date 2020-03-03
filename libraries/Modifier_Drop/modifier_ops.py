import bpy
from .bp_lib import bp_utils
from . import modifier_library

class MODIFIER_OT_drop_modifier(bpy.types.Operator):
    bl_idname = "modifier.drop_modifier"
    bl_label = "Drop Modifier"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")
    
    @classmethod
    def poll(cls, context):
        return True
        
    def execute(self, context):
        # self.mat = self.get_material(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        context.window.cursor_set('PAINT_BRUSH')
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        selected_point, selected_obj = bp_utils.get_selection_point(context,event)
        bpy.ops.object.select_all(action='DESELECT')
        if selected_obj:
            selected_obj.select_set(True)
            context.view_layer.objects.active = selected_obj
        
            if self.event_is_place_modifier(event):
                selected_obj["PROMPT_ID"] = "modifier.prompts"
                print("FP --- ",self.filepath)
                array = modifier_library.Array()
                array.add_modifier(selected_obj)

                return self.finish(context)

        if self.event_is_cancel_command(event):
            return self.cancel_drop(context)
        
        if self.event_is_pass_through(event):
            return {'PASS_THROUGH'}        
        
        return {'RUNNING_MODAL'}

    def event_is_place_modifier(self,event):
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
        context.window.cursor_set('DEFAULT')
        return {'CANCELLED'}
    
    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        context.area.tag_redraw()
        bpy.ops.modifier.prompts('INVOKE_DEFAULT')
        return {'FINISHED'}

class MODIFIER_OT_save_current_modifier_stack_to_library(bpy.types.Operator):
    bl_idname = "modifier.save_current_modifier_stack_to_library"
    bl_label = "Save Current Modifier Stack to Library"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")
    
    @classmethod
    def poll(cls, context):
        return True
        
    def execute(self, context):
        return {'FINISHED'}

bpy.utils.register_class(MODIFIER_OT_drop_modifier)
bpy.utils.register_class(MODIFIER_OT_save_current_modifier_stack_to_library)      