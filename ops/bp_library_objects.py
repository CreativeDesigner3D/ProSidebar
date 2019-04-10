import bpy
from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        UIList,
        )
from bpy.props import (
        BoolProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        CollectionProperty,
        )
import gpu
from gpu_extras.batch import batch_for_shader
import math, random
from bpy_extras import view3d_utils
import mathutils
from mathutils import Vector
from ..bp_lib import ui_bgl
from ..bp_lib import bp_utils

def draw_callback_2d(self,context):
    ui_bgl.draw_rect(self.library_menu_x, 10, 200, 750, (1, 1, 1, .05))

def mouse_in_asset_panel(mx, my):
    ui_props = bpy.context.scene.blenderkitUI
    if ui_props.bar_y < my < ui_props.bar_y + ui_props.bar_height \
            and mx > ui_props.bar_x and mx < ui_props.bar_x + ui_props.bar_width:
        return True
    else:
        return False

class BP_OT_object_library(Operator):
    bl_idname = "bp.object_library"
    bl_label = "Object Library"
    bl_description = "Activate Object Library"
    bl_options = {'REGISTER', 'UNDO'}
 
    region = None
    _draw_handle = None
    coords = []
    shader = None
    batch = None

    snapped_location: FloatVectorProperty(name="snapped_location", default=(0, 0, 0))
    has_hit: BoolProperty(name="has_hit", default=False)
    snapped_normal: FloatVectorProperty(name="snapped_normal", default=(0, 0, 0))
    snapped_rotation: FloatVectorProperty(name="snapped_rotation", default=(0, 0, 0), subtype='QUATERNION')

    library_menu_x = 0

    def modal(self, context, event):
        

        if context.region != self.region:
            print('CONTEXT PASS')
            return {'PASS_THROUGH'}

        mx = event.mouse_x - self.region.x
        my = event.mouse_y - self.region.y
        margin = 20

        for r in context.area.regions:
            if r.type == 'TOOLS':
                self.library_menu_x = r.width + margin 

        self.has_hit, self.snapped_location, self.snapped_normal, self.snapped_rotation, face_index, obj, matrix = bp_utils.floor_raycast(context, mx, my)

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            pass
            
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_2d, 'WINDOW')
            context.area.tag_redraw()
            return {'FINISHED'}

        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        
        context.area.tag_redraw()
        return {'PASS_THROUGH'}
 
    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            # the arguments we pass the the callback
            args = (self, context)
            self.rv3d = context.region_data
            self.area = context.area
            self.scene = bpy.context.scene

            for r in self.area.regions:
                if r.type == 'WINDOW':
                    self.region = r

            self._handle_2d = bpy.types.SpaceView3D.draw_handler_add(draw_callback_2d, args, 'WINDOW', 'POST_PIXEL')
            # self._handle_3d = bpy.types.SpaceView3D.draw_handler_add(draw_callback_3d, args, 'WINDOW', 'POST_VIEW')

            context.window_manager.modal_handler_add(self)
            context.area.tag_redraw() 
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

    def execute(self, context):
        return {'RUNNING_MODAL'}       


classes = (
    BP_OT_object_library,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    # bpy.utils.register_tool('VIEW_3D', 'OBJECT', object_library_tool) HOW DO I CREATE A ACTIVE TOOL


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    # bpy.utils.unregister_tool('VIEW_3D', 'OBJECT', object_library_tool)

# register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()        