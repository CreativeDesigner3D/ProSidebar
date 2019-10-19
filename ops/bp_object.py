import bpy
from bpy.types import Header, Menu, Operator, UIList, PropertyGroup
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       BoolVectorProperty,
                       PointerProperty,
                       EnumProperty,
                       CollectionProperty)
import os
from ..bp_lib import bp_unit, bp_utils

class bp_object_OT_select_object(bpy.types.Operator):
    bl_idname = "bp_object.select_object"
    bl_label = "Select Object"
    bl_options = {'UNDO'}

    obj_name: StringProperty(name='Object Name')

    def execute(self, context):
        if self.obj_name in context.scene.objects:
            bpy.ops.object.select_all(action = 'DESELECT')
            obj = context.scene.objects[self.obj_name]
            obj.select_set(True)
            context.view_layer.objects.active = obj
        return {'FINISHED'}

class bp_object_OT_collapse_all_modifiers(Operator):
    bl_idname = "bp_object.collapse_all_modifiers"
    bl_label = "Collapse All Modifiers"
    bl_description = "Collapse all modifiers in the modifiers stack"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.object

    def execute(self, context):
        if context.object.type == 'GPENCIL':
            for mod in context.active_object.grease_pencil_modifiers:
                mod.show_expanded = False
        else:
            for mod in context.active_object.modifiers:
                mod.show_expanded = False

        return {'FINISHED'}
    
class bp_object_OT_collapse_all_constraints(Operator):
    bl_idname = "bp_object.collapse_all_constraints"
    bl_label = "Collapse All Constraints"
    bl_description = "Collapse all constraints in the modifiers stack"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.object

    def execute(self, context):
        for con in context.active_object.constraints:
            con.show_expanded = False
        return {'FINISHED'}

class bp_object_OT_add_text(bpy.types.Operator):
    bl_idname = "bp_object.add_text_dialog"
    bl_label = "Add Text"
    bl_description = "Adds text to the scene with the ability to set the text and split by a character"
    
    enter_text: StringProperty(name='Enter Text')
    split_with: StringProperty(name='Split With')
    split_text_with_character: BoolProperty(name="Split Text with Character")

    def check(self, context):
        return True

    def execute(self, context):
        if self.split_with != "":
            objs = []
            split_text = self.enter_text.split(self.split_with)
            current_y = 0
            for text in split_text:
                bpy.ops.object.text_add()
                obj = context.active_object
                obj.name = text
                obj.data.body = text
                obj.location.y = current_y
                obj.select_set(True)
                current_y -= obj.dimensions.y
                objs.append(obj)
            bpy.ops.object.select_all(action='DESELECT')
            for obj in objs:
                obj.select_set(True)
        else:
            bpy.ops.object.text_add()
            obj = context.active_object
            obj.name = self.enter_text
            obj.data.body = self.enter_text
            obj.select_set(True)
        return {'FINISHED'}
        
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)
        
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self,"enter_text")
        col.prop(self,"split_text_with_character")
        if self.split_text_with_character:
            col.prop(self,"split_with",text="Enter Character")

class bp_object_OT_add_camera(bpy.types.Operator):
    bl_idname = "bp_object.add_camera"
    bl_label = "Add Camera"
    bl_description = "Adds a camera aligned to the view"
    bl_options = {'UNDO'}

    def execute(self, context):
        bpy.ops.object.camera_add(align='VIEW')
        camera = context.active_object
        bpy.ops.view3d.camera_to_view()
        camera.data.clip_start = bp_unit.inch(1)
        camera.data.clip_end = 9999
        camera.data.ortho_scale = 200.0
        return {'FINISHED'}

def update_particle_paint_name(self,context):
    for i, particle in enumerate(self.particle_systems):
        if particle:
            self.group_name = bpy.data.particles[i].name

class bp_object_OT_particle_paint(bpy.types.Operator):
    bl_idname = "bp_object.particle_paint"
    bl_label = "Particle Paint"

    particle_systems: bpy.props.BoolVectorProperty(name="Particle Systems", 
                                                    description="Determines if the particle system is set to draw", 
                                                    size=32,
                                                    update=update_particle_paint_name)

    group_name: bpy.props.StringProperty(name="Group Name")

    def check(self, context):
        return True

    @classmethod
    def poll(cls, context):
        if context.object and len(bpy.data.particles) > 0:
            return True
        else:
            return False

    def execute(self, context):
        particle = None
        for i, particle in enumerate(self.particle_systems):
            if particle:
                particle_settings = bpy.data.particles[i]
                
        obj = context.object
        vgrp = obj.vertex_groups.new(name=self.group_name)
        mod = obj.modifiers.new(self.group_name,'PARTICLE_SYSTEM')
        mod.particle_system.settings = particle_settings
        mod.particle_system.vertex_group_density = self.group_name
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT') 
        #GET SELECTED SETTINGS
        #mod.settings = bpy.data.particles[name]
        return {'FINISHED'}
        
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)
        
    def draw(self, context):
        layout = self.layout
        layout.label(text="Select the Particles to Draw:")
        for i, particle in enumerate(bpy.data.particles):
            row = layout.row()
            row.prop(self,'particle_systems',index=i,text="")
            row.label(text=particle.name)
        layout.prop(self,'group_name',text="Particle Name")


class bp_object_OT_toggle_edit_mode(Operator):
    bl_idname = "bp_object.toggle_edit_mode"
    bl_label = "Toggle Edit Mode"
    bl_description = "This will toggle between object and edit mode"
    
    obj_name: StringProperty(name="Object Name")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = bpy.data.objects[self.obj_name]
        obj.hide_set(False)
        obj.hide_select = False
        obj.select_set(True)
        context.view_layer.objects.active = obj
        bpy.ops.object.editmode_toggle()
        return {'FINISHED'}


class bp_object_OT_update_selected_text_with_active_font(bpy.types.Operator):
    bl_idname = "bp_object.update_selected_text_with_active_font"
    bl_label = "Update Selected Text with Active Font"

    def execute(self, context):
        active_font = context.active_object.data.font
        for obj in context.selected_objects:
            obj.data.font = active_font
        return {'FINISHED'}


class bp_object_OT_place_area_lamp(bpy.types.Operator):
    bl_idname = "bp_object.place_area_lamp"
    bl_label = "Place Area Lamp"
    bl_options = {'UNDO'}
    
    #READONLY
    _draw_handle = None
    mouse_x = 0
    mouse_y = 0
    
    drawing_plane = None
    lamp = None
    ray_cast_objects = []
    placed_first_point = False
    selected_point = (0,0,0)
    
    @classmethod
    def poll(cls, context):
        active_col = context.view_layer.active_layer_collection.collection
        if active_col.hide_viewport:
            return False        
        if context.object and context.object.mode != 'OBJECT':
            return False
        return True

    def cancel_drop(self,context):
        bp_utils.delete_object_and_children(self.lamp)
        self.finish(context)
        
    def finish(self,context):
        context.space_data.draw_handler_remove(self._draw_handle, 'WINDOW')
        context.window.cursor_set('DEFAULT')
        if self.drawing_plane:
            bp_utils.delete_obj_list([self.drawing_plane])
        context.area.tag_redraw()
        return {'FINISHED'}

    @staticmethod
    def _window_region(context):
        window_regions = [region
                          for region in context.area.regions
                          if region.type == 'WINDOW']
        return window_regions[0]

    def draw_opengl(self,context):     
        region = self._window_region(context)
        
        # help_box = TextBox(
        #     x=0,y=0,
        #     width=500,height=0,
        #     border=10,margin=100,
        #     message="Command Help:\nLEFT CLICK: Place Wall\nRIGHT CLICK: Cancel Command")
        # help_box.x = (self.mouse_x + (help_box.width) / 2 + 10) - region.x
        # help_box.y = (self.mouse_y - 10) - region.y

        # help_box.draw()

    def event_is_place_first_point(self,event):
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and self.placed_first_point == False:
            return True
        elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS' and self.placed_first_point == False:
            return True
        elif event.type == 'RET' and event.value == 'PRESS' and self.placed_first_point == False:
            return True
        else:
            return False

    def event_is_place_second_point(self,event):
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and self.placed_first_point:
            return True
        elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS' and self.placed_first_point:
            return True
        elif event.type == 'RET' and event.value == 'PRESS' and self.placed_first_point:
            return True
        else:
            return False

    def position_lamp(self,selected_point):
        if not self.placed_first_point:
            self.lamp.location = selected_point
            self.selected_point = selected_point
        else:
            self.lamp.data.size = bp_utils.calc_distance((self.selected_point[0],0,0),(selected_point[0],0,0))
            self.lamp.data.size_y = bp_utils.calc_distance((0,self.selected_point[1],0),(0,selected_point[1],0))
            self.lamp.location.x = self.selected_point[0] + ((selected_point[0]/2) - (self.selected_point[0]/2))
            self.lamp.location.y = self.selected_point[1] + ((selected_point[1]/2) - (self.selected_point[1]/2))
            self.lamp.location.z = self.selected_point[2]
#             self.lamp.x_dim(value = selected_point[0] - self.selected_point[0])
#             self.lamp.y_dim(value = selected_point[1] - self.selected_point[1])
#             self.lamp.z_dim(value = selected_point[2] - self.selected_point[2])
            
    def modal(self, context, event):
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        
        selected_point, selected_obj = bp_utils.get_selection_point(context,event)
        
        self.position_lamp(selected_point)
        
        if self.event_is_place_second_point(event):
            return self.finish(context)

        if self.event_is_place_first_point(event):
            self.placed_first_point = True

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel_drop(context)
            return {'CANCELLED'}
        
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}        
        
        return {'RUNNING_MODAL'}
        
    def create_drawing_plane(self,context):
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.display_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)
        self.ray_cast_objects.append(self.drawing_plane)

    def invoke(self, context, event):
        self.ray_cast_objects = []
        # for obj in bpy.data.objects:
        #     if ISWALL in obj or ISROOMMESH in obj:
        #         self.ray_cast_objects.append(obj)
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        self._draw_handle = context.space_data.draw_handler_add(
            self.draw_opengl, (context,), 'WINDOW', 'POST_PIXEL')
        self.placed_first_point = False
        self.selected_point = (0,0,0)
        
        self.create_drawing_plane(context)
        
        lamp = bpy.data.lights.new("Room Lamp",'AREA')
        lamp.shape = 'RECTANGLE'
        obj_lamp = bpy.data.objects.new("Room Lamp", lamp)
        context.view_layer.active_layer_collection.collection.objects.link(obj_lamp)
        # context.scene.objects.link(obj_lamp)
        self.lamp = obj_lamp
        self.lamp.data.use_nodes = True
#         bpy.ops.cycles.use_shading_nodes()
        
        #CREATE CUBE
#         self.cube = Assembly()
#         self.cube.create_assembly()
#         mesh_obj = self.cube.add_mesh("RoomCube")
#         mesh_obj[ISROOMMESH] = True
#         self.cube.x_dim(value = 0)
#         self.cube.y_dim(value = 0)
#         self.cube.z_dim(value = 0)
        
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}


class bp_object_OT_set_base_point(bpy.types.Operator):
    bl_idname = "bp_object.set_base_point"
    bl_label = "Set Base Point"
    bl_options = {'UNDO'}

    object_name = bpy.props.StringProperty(name="Object Name")

    def execute(self, context):
        obj = context.object
        # obj = bpy.data.objects[self.object_name]
        cursor_x = context.scene.cursor.location[0]
        cursor_y = context.scene.cursor.location[1]
        cursor_z = context.scene.cursor.location[2]
        bpy.ops.view3d.snap_cursor_to_selected()
        if obj.mode == 'EDIT':
            bpy.ops.object.editmode_toggle()
            
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        context.scene.cursor.location = (cursor_x,cursor_y,cursor_z)
        if obj.mode == 'OBJECT':
            bpy.ops.object.editmode_toggle()
            
        return {'FINISHED'}    

classes = (
    bp_object_OT_select_object,
    bp_object_OT_collapse_all_modifiers,
    bp_object_OT_collapse_all_constraints,
    bp_object_OT_add_text,
    bp_object_OT_add_camera,
    bp_object_OT_particle_paint,
    bp_object_OT_toggle_edit_mode,
    bp_object_OT_update_selected_text_with_active_font,
    bp_object_OT_place_area_lamp,
    bp_object_OT_set_base_point
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                