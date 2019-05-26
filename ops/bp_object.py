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
from ..bp_lib import bp_unit

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
    bl_options = {'UNDO'}

    def execute(self, context):
        bpy.ops.object.camera_add(view_align=False)
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

classes = (
    bp_object_OT_select_object,
    bp_object_OT_collapse_all_modifiers,
    bp_object_OT_collapse_all_constraints,
    bp_object_OT_add_text,
    bp_object_OT_add_camera,
    bp_object_OT_particle_paint,
    bp_object_OT_toggle_edit_mode
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                