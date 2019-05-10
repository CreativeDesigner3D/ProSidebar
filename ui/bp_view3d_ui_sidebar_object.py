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
        IntProperty,
        PointerProperty,
        StringProperty,
        CollectionProperty,
        )
import math        
from .modifiers import Modifier, Gpencil_Modifier
from .constraints import Constraint
from ..bp_lib import bp_unit, bp_utils, bp_types

#TODO: IMPLEMENT OBJECT DATA
#TODO: FIGURE OUT HOW TO IMPLEMENT INFO FOR GREASE PENCIL (LAYERS, MATERIALS, ...)
#TODO: IMPLEMENT CONSTRAINTS PANEL
#TODO: IMPLEMENT DIFFERENT MODES OR REMOVE THEM


class VIEW3D_PT_objects(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Object"
    bl_category = "Object"
    bl_options = {'HIDE_HEADER'}
    
    def draw_modes(self,obj,layout):
        row = layout.row(align=True)
        row.scale_y = 1.3        
        if obj.type == 'MESH':
            row.operator('object.mode_set',text="Object",icon = 'CHECKBOX_HLT' if obj.mode == 'OBJECT' else 'BLANK1').mode = 'OBJECT'
            row.operator('object.mode_set',text="Edit",icon = 'CHECKBOX_HLT' if obj.mode == 'EDIT' else 'BLANK1').mode = 'EDIT'
            row.operator('object.mode_set',text="Sculpt",icon = 'CHECKBOX_HLT' if obj.mode == 'SCULPT' else 'BLANK1').mode = 'SCULPT'

        if obj.type in {'CURVE','FONT','LATTICE','META','SURFACE'}:
            row.operator('object.mode_set',text="Object",icon = 'CHECKBOX_HLT' if obj.mode == 'OBJECT' else 'BLANK1').mode = 'OBJECT'
            row.operator('object.mode_set',text="Edit",icon = 'CHECKBOX_HLT' if obj.mode == 'EDIT' else 'BLANK1').mode = 'EDIT'

        if obj.type in {'EMPTY','LIGHT','CAMERA','SPEAKER','FORCE_FIELD','LIGHT_PROBE'}:
            row.operator('object.mode_set',text="Object",icon = 'CHECKBOX_HLT' if obj.mode == 'OBJECT' else 'BLANK1').mode = 'OBJECT'
                                    
        if obj.type == 'ARMATURE':
            row.operator('object.mode_set',text="Object",icon = 'CHECKBOX_HLT' if obj.mode == 'OBJECT' else 'BLANK1').mode = 'OBJECT'
            row.operator('object.mode_set',text="Edit",icon = 'CHECKBOX_HLT' if obj.mode == 'EDIT' else 'BLANK1').mode = 'EDIT'
            row.operator('object.mode_set',text="Pose",icon = 'CHECKBOX_HLT' if obj.mode == 'POSE' else 'BLANK1').mode = 'POSE'

        if obj.type == 'GPENCIL':
            row.operator('object.mode_set',text="Object",icon = 'CHECKBOX_HLT' if obj.mode == 'OBJECT' else 'BLANK1').mode = 'OBJECT'
            row.operator('object.mode_set',text="Edit",icon = 'CHECKBOX_HLT' if obj.mode == 'EDIT_GPENCIL' else 'BLANK1').mode = 'EDIT_GPENCIL'
            row.operator('object.mode_set',text="Draw",icon = 'CHECKBOX_HLT' if obj.mode == 'PAINT_GPENCIL' else 'BLANK1').mode = 'PAINT_GPENCIL'
            row.operator('object.mode_set',text="Sculpt",icon = 'CHECKBOX_HLT' if obj.mode == 'SCULPT_GPENCIL' else 'BLANK1').mode = 'SCULPT_GPENCIL'

    def draw(self, context):
        obj = context.object
        layout = self.layout
        
        row = layout.row(align=True)
        row.scale_y = 1.3
        row.operator("library.add_object_from_library",text="Object Library",icon='DISK_DRIVE')
        row.menu('LIBRARY_MT_object_library',text="",icon="DISCLOSURE_TRI_DOWN")

        if obj:
            self.draw_modes(obj,layout)
            row = layout.row(align=True)
            row.scale_y = 1.3
            split = row.split(factor=.7,align=True)
            split.popover(panel="VIEW3D_PT_object_selection",text=obj.name,icon=bp_utils.get_object_icon(obj))
            split.menu("VIEW3D_MT_bp_add", text="Add",icon='ADD')
            layout.prop(obj,'name')
        else:
            row = layout.row(align=True)
            row.scale_y = 1.3            
            row.menu("VIEW3D_MT_bp_add", text="Add",icon='ADD')


class SCENE_UL_objects(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name,icon=bp_utils.get_object_icon(item))
        layout.prop(item,'hide_viewport',emboss=False,icon_only=True)
        layout.prop(item,'hide_select',emboss=False,icon_only=True)
        layout.prop(item,'hide_render',emboss=False,icon_only=True)


class VIEW3D_PT_object_selection(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_label = "Object Selection"
    bl_ui_units_x = 18

    def draw(self, context):
        layout = self.layout
        layout.template_list("SCENE_UL_objects", "", context.scene, "objects", context.scene.bp_props, "selected_object_index", rows=4)    


class VIEW3D_PT_object_transform(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Transform"
    bl_category = "Object"
    # bl_parent_id = 'VIEW3D_PT_objects'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return context.object
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text='',icon='ORIENTATION_GIMBAL')

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if obj.type not in {'EMPTY','CAMERA','LIGHT'}:
            col = layout.column(align=True)
            col.label(text='Dimensions:')
            #X
            row = col.row(align=True)
            row.prop(obj,"lock_scale",index=0,text="")
            if obj.lock_scale[0]:
                row.label(text="X: " + str(round(bp_unit.meter_to_active_unit(obj.dimensions.x),4)))
            else:
                row.prop(obj,"dimensions",index=0,text="X")
            #Y
            row = col.row(align=True)
            row.prop(obj,"lock_scale",index=1,text="")
            if obj.lock_scale[1]:
                row.label(text="Y: " + str(round(bp_unit.meter_to_active_unit(obj.dimensions.y),4)))
            else:
                row.prop(obj,"dimensions",index=1,text="Y")
            #Z
            row = col.row(align=True)
            row.prop(obj,"lock_scale",index=2,text="")
            if obj.lock_scale[2]:
                row.label(text="Z: " + str(round(bp_unit.meter_to_active_unit(obj.dimensions.z),4)))
            else:
                row.prop(obj,"dimensions",index=2,text="Z")

        if obj.type == 'CAMERA':
            cam = obj.data
            row = layout.row()
            row.label(text="Size:")
            row.prop(cam, "display_size", text="")

        if obj.type == 'EMPTY':
            row = layout.row()
            row.label(text="Size:")            
            row.prop(obj, "empty_display_size", text="")            

        col1 = layout.row()
        col2 = col1.split()
        col = col2.column(align=True)
        col.label(text='Location:')
        #X
        row = col.row(align=True)
        row.prop(obj,"lock_location",index=0,text="")
        if obj.lock_location[0]:
            row.label(text="X: " + str(round(bp_unit.meter_to_active_unit(obj.location.x),4)))
        else:
            row.prop(obj,"location",index=0,text="X")
        #Y    
        row = col.row(align=True)
        row.prop(obj,"lock_location",index=1,text="")
        if obj.lock_location[1]:
            row.label(text="Y: " + str(round(bp_unit.meter_to_active_unit(obj.location.y),4)))
        else:
            row.prop(obj,"location",index=1,text="Y")
        #Z    
        row = col.row(align=True)
        row.prop(obj,"lock_location",index=2,text="")
        if obj.lock_location[2]:
            row.label(text="Z: " + str(round(bp_unit.meter_to_active_unit(obj.location.z),4)))
        else:
            row.prop(obj,"location",index=2,text="Z")
            
        col2 = col1.split()
        col = col2.column(align=True)
        col.label(text='Rotation:')
        #X
        row = col.row(align=True)
        row.prop(obj,"lock_rotation",index=0,text="")
        if obj.lock_rotation[0]:
            row.label(text="X: " + str(round(math.degrees(obj.rotation_euler.x),4)))
        else:
            row.prop(obj,"rotation_euler",index=0,text="X")
        #Y    
        row = col.row(align=True)
        row.prop(obj,"lock_rotation",index=1,text="")
        if obj.lock_rotation[1]:
            row.label(text="Y: " + str(round(math.degrees(obj.rotation_euler.y),4)))
        else:
            row.prop(obj,"rotation_euler",index=1,text="Y")
        #Z    
        row = col.row(align=True)
        row.prop(obj,"lock_rotation",index=2,text="")
        if obj.lock_rotation[2]:
            row.label(text="Y: " + str(round(math.degrees(obj.rotation_euler.z),4)))
        else:
            row.prop(obj,"rotation_euler",index=2,text="Z")


class VIEW3D_PT_object_material(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Materials"
    bl_category = "Object"
    # bl_parent_id = 'VIEW3D_PT_objects'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return context.object
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text='',icon='MATERIAL')

    def draw_gpencil_properties(self,context,layout,obj):
        mat = obj.material_slots[obj.active_material_index].material
        if mat is not None and mat.grease_pencil is not None:
            gpcolor = mat.grease_pencil
            box = layout.box()
            row = box.row()
            row.label(text="",icon='SOLO_OFF')
            row.prop(gpcolor, "show_stroke")
            row = box.row(align=True)
            row.label(text="Line Type:")
            row.prop(gpcolor, "mode",text="")
            row.prop(gpcolor, "stroke_style", text="")

            if gpcolor.stroke_style == 'TEXTURE':
                row = box.row()
                row.enabled = not gpcolor.lock
                box = row.column(align=True)
                box.template_ID(gpcolor, "stroke_image", open="image.open")
                if gpcolor.mode == 'LINE':
                    box.prop(gpcolor, "pixel_size", text="UV Factor")

                box.prop(gpcolor, "use_stroke_pattern", text="Use As Pattern")

            if gpcolor.stroke_style == 'SOLID' or gpcolor.use_stroke_pattern is True:
                row = box.row()
                row.label(text="Color:")
                row.prop(gpcolor, "color", text="")

            if gpcolor.mode in {'DOTS', 'BOX'}:
                box.prop(gpcolor, "use_follow_path", text="Follow Drawing Path")

            box = layout.box()
            row = box.row()
            row.label(text="",icon='SOLO_ON')            
            row.prop(gpcolor, "show_fill")
            col = box.column()
            col.active = not gpcolor.lock
            col.prop(gpcolor, "fill_style", text="Style")

            if gpcolor.fill_style == 'GRADIENT':
                col.prop(gpcolor, "gradient_type")

            if gpcolor.fill_style != 'TEXTURE':
                row = col.row()
                row.label(text="Color:")
                row.prop(gpcolor, "fill_color", text="")

                if gpcolor.fill_style in {'GRADIENT', 'CHESSBOARD'}:
                    col.prop(gpcolor, "mix_color", text="Secondary Color")

                if gpcolor.fill_style == 'GRADIENT':
                    col.prop(gpcolor, "mix_factor", text="Mix Factor", slider=True)

                if gpcolor.fill_style in {'GRADIENT', 'CHESSBOARD'}:
                    col.prop(gpcolor, "flip", text="Flip Colors")

                    col.prop(gpcolor, "pattern_shift", text="Location")
                    col.prop(gpcolor, "pattern_scale", text="Scale")

                if gpcolor.gradient_type == 'RADIAL' and gpcolor.fill_style not in {'SOLID', 'CHESSBOARD'}:
                    col.prop(gpcolor, "pattern_radius", text="Radius")
                else:
                    if gpcolor.fill_style != 'SOLID':
                        col.prop(gpcolor, "pattern_angle", text="Angle")

                if gpcolor.fill_style == 'CHESSBOARD':
                    col.prop(gpcolor, "pattern_gridsize", text="Box Size")

            # Texture
            if gpcolor.fill_style == 'TEXTURE' or (gpcolor.texture_mix is True and gpcolor.fill_style == 'SOLID'):
                col.template_ID(gpcolor, "fill_image", open="image.open")

                if gpcolor.fill_style == 'TEXTURE':
                    col.prop(gpcolor, "use_fill_pattern", text="Use As Pattern")
                    if gpcolor.use_fill_pattern is True:
                        col.prop(gpcolor, "fill_color", text="Color")

                col.prop(gpcolor, "texture_offset", text="Offset")
                col.prop(gpcolor, "texture_scale", text="Scale")
                col.prop(gpcolor, "texture_angle")
                col.prop(gpcolor, "texture_opacity")
                col.prop(gpcolor, "texture_clamp", text="Clip Image")

                if gpcolor.use_fill_pattern is False:
                    col.prop(gpcolor, "texture_mix", text="Mix With Color")

                    if gpcolor.texture_mix is True:
                        col.prop(gpcolor, "fill_color", text="Mix Color")
                        col.prop(gpcolor, "mix_factor", text="Mix Factor", slider=True)

    def draw(self, context):
        layout = self.layout
        obj = context.object
        slot = None
        if len(obj.material_slots) - 1 > obj.active_material_index:
            slot = obj.material_slots[obj.active_material_index]

        is_sortable = len(obj.material_slots) > 1
        rows = 3
        if (is_sortable):
            rows = 5

        row = layout.row()

        if obj.type == 'GPENCIL':
            row.template_list("GPENCIL_UL_matslots", "", obj, "material_slots", obj, "active_material_index", rows=rows)
        else:
            row.template_list("MATERIAL_UL_matslots", "", obj, "material_slots", obj, "active_material_index", rows=rows)

        col = row.column(align=True)
        col.operator("object.material_slot_add", icon='ADD', text="")
        col.operator("object.material_slot_remove", icon='REMOVE', text="")

        col.separator()

        col.menu("MATERIAL_MT_context_menu", icon='DOWNARROW_HLT', text="")

        if is_sortable:
            col.separator()

            col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        row = layout.row()

        row.template_ID(obj, "active_material", new="material.new")

        if slot:
            icon_link = 'MESH_DATA' if slot.link == 'DATA' else 'OBJECT_DATA'
            row.prop(slot, "link", icon=icon_link, icon_only=True)

        if obj.mode == 'EDIT':
            row = layout.row(align=True)
            row.operator("object.material_slot_assign", text="Assign")
            row.operator("object.material_slot_select", text="Select")
            row.operator("object.material_slot_deselect", text="Deselect")

        if obj.type == 'GPENCIL':
            self.draw_gpencil_properties(context,layout,obj)
        else:
            layout.operator("bp_general.open_new_editor",text="Open Material Editor",icon='MATERIAL').space_type = 'NODE_EDITOR'


class VIEW3D_PT_object_modifiers(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Modifiers"
    bl_category = "Object"
    # bl_parent_id = 'VIEW3D_PT_objects'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return context.object
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text='',icon='MODIFIER')

    def draw(self, context):
        layout = self.layout
        obj = context.object        

        if obj.type == 'GPENCIL':
            col = layout.column(align=True)
            row = col.row()            
            row.operator_menu_enum("object.gpencil_modifier_add", "type")
            row.operator('bp_object.collapse_all_modifiers',text="",icon='FULLSCREEN_EXIT')

            for md in obj.grease_pencil_modifiers:
                box = col.template_greasepencil_modifier(md)
                if box:
                    # match enum type to our functions, avoids a lookup table.
                    getattr(Gpencil_Modifier, md.type)(Gpencil_Modifier, box, obj, md)
        else:

            col = layout.column(align=True)
            row = col.row()
            row.operator_menu_enum("object.modifier_add", "type")
            row.operator('bp_object.collapse_all_modifiers',text="",icon='FULLSCREEN_EXIT')
            
            col.separator()

            for mod in obj.modifiers:
                box = col.template_modifier(mod)
                if box:
                    # match enum type to our functions, avoids a lookup table.
                    getattr(Modifier, mod.type)(None, box, obj, mod)


class VIEW3D_PT_object_view_options(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "View Options"
    bl_category = "Object"
    # bl_parent_id = 'VIEW3D_PT_objects'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return context.object
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text='',icon='HIDE_OFF')
    
    def draw(self, context):
        layout = self.layout
        obj = context.object          
        row = layout.row()
        row.prop(obj,'display_type',expand=True)
        row = layout.row()
        # row.prop(obj,'hide_select')
        row.prop(obj,'hide_viewport')
        row.prop(obj,'hide_render')


class VIEW3D_PT_object_constraints(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Constraints"
    bl_category = "Object"
    # bl_parent_id = 'VIEW3D_PT_objects'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return context.object
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text='',icon='CONSTRAINT')

    def draw(self, context):
        layout = self.layout
        obj = context.object
        col = layout.column(align=True)
        row = col.row()
        row.operator_menu_enum("object.constraint_add", "type", text="Add Object Constraint")
        row.operator('bp_object.collapse_all_constraints',text="",icon='FULLSCREEN_EXIT')
        
        col.separator()

        for con in obj.constraints:

            box = col.template_constraint(con)

            if box:
                # match enum type to our functions, avoids a lookup table.
                getattr(Constraint, con.type)(Constraint, context, box, con)

                if con.type not in {'RIGID_BODY_JOINT', 'NULL'}:
                    box.prop(con, "influence")

class VIEW3D_PT_object_data(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Object Data"
    bl_category = "Object"
    # bl_parent_id = 'VIEW3D_PT_objects'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return context.object
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text='',icon=bp_utils.get_object_icon(context.object))

    def draw_uv_maps(self,layout,obj):
        me = obj.data
        uv_map_col = layout.column(align=True)
        box = uv_map_col.box()
        row = box.row()
        row.label(text="UV Maps",icon='GROUP_UVS')
        
        if len(me.uv_layers) > 0:
            row.operator('bp_general.open_texture_editor',
                            text="Show UV Map",
                            icon='UV')    

            row = box.row()
            col = row.column()

            col.template_list("MESH_UL_uvmaps", "uvmaps", me, "uv_layers", me.uv_layers, "active_index", rows=1)
        
            col = row.column(align=True)
            col.operator("mesh.uv_texture_add", icon='ADD', text="")
            col.operator("mesh.uv_texture_remove", icon='REMOVE', text="")    
        else:
            row.operator('uv.smart_project',icon='ADD',text="Unwrap Mesh")

    def draw_vertex_groups(self,layout,obj):
        group = obj.vertex_groups.active

        rows = 2
        if group:
            rows = 4
        
        box = layout.box()
        row = box.row()
        row.label(text="Vertex Groups:",icon='GROUP_VERTEX')
        if len(obj.vertex_groups) > 0:
            row = box.row()
            row.template_list("MESH_UL_vgroups", "", obj, "vertex_groups", obj.vertex_groups, "active_index", rows=rows)
        
            col = row.column(align=True)
            col.operator("object.vertex_group_add", icon='ADD', text="")
            col.operator("object.vertex_group_remove", icon='REMOVE', text="").all = False
            col.menu("MESH_MT_vertex_group_context_menu", icon='DOWNARROW_HLT', text="")
            if group:
                col.separator()
                col.operator("object.vertex_group_move", icon='TRIA_UP', text="").direction = 'UP'
                col.operator("object.vertex_group_move", icon='TRIA_DOWN', text="").direction = 'DOWN'
        
            if obj.vertex_groups and (obj.mode == 'EDIT' or (obj.mode == 'WEIGHT_PAINT' and obj.type == 'MESH' and obj.data.use_paint_mask_vertex)):
                row = box.row()
        
                sub = row.row(align=True)
                sub.operator("object.vertex_group_assign", text="Assign")
                sub.operator("object.vertex_group_remove_from", text="Remove")
        
                sub = row.row(align=True)
                sub.operator("object.vertex_group_select", text="Select")
                sub.operator("object.vertex_group_deselect", text="Deselect")
        
                box.prop(bpy.context.tool_settings, "vertex_group_weight", text="Weight")   
        else:
            row.operator('object.vertex_group_add',icon='ADD',text="Add")        

    def draw_shape_keys(self,layout,obj):
        key = obj.data.shape_keys
        kb = obj.active_shape_key

        enable_edit = obj.mode != 'EDIT'
        enable_edit_value = False

        if obj.show_only_shape_key is False:
            if enable_edit or (obj.type == 'MESH' and obj.use_shape_key_edit_mode):
                enable_edit_value = True
                
        box = layout.box()
        row = box.row()
        row.label(text="Shape Keys",icon='SHAPEKEY_DATA')
        
        if key and len(key.key_blocks) > 0:
            row = box.row()
            rows = 2
            if kb:
                rows = 4
            row.template_list("MESH_UL_shape_keys", "", key, "key_blocks", obj, "active_shape_key_index", rows=rows)
        
            col = row.column()
        
            sub = col.column(align=True)
            sub.operator("object.shape_key_add", icon='ADD', text="").from_mix = False
            sub.operator("object.shape_key_remove", icon='REMOVE', text="").all = False
            sub.menu("MESH_MT_shape_key_specials", icon='DOWNARROW_HLT', text="")
        
            if kb:
                col.separator()
        
                sub = col.column(align=True)
                sub.operator("object.shape_key_move", icon='TRIA_UP', text="").type = 'UP'
                sub.operator("object.shape_key_move", icon='TRIA_DOWN', text="").type = 'DOWN'
        
                split = box.split(factor=0.4)
                row = split.row()
                row.enabled = enable_edit
                row.prop(key, "use_relative")
        
                row = split.row()
                row.alignment = 'RIGHT'
        
                sub = row.row(align=True)
                sub.label()  # XXX, for alignment only
                subsub = sub.row(align=True)
                subsub.active = enable_edit_value
                subsub.prop(obj, "show_only_shape_key", text="")
                sub.prop(obj, "use_shape_key_edit_mode", text="")
        
                sub = row.row()
                if key.use_relative:
                    sub.operator("object.shape_key_clear", icon='REMOVE', text="")
                else:
                    sub.operator("object.shape_key_retime", icon='RECOVER_LAST', text="")
        
                if key.use_relative:
                    if obj.active_shape_key_index != 0:
                        row = box.row()
                        row.active = enable_edit_value
                        row.prop(kb, "value")
        
                        split = box.split()
        
                        col = split.column(align=True)
                        col.active = enable_edit_value
                        col.label(text="Range:")
                        col.prop(kb, "slider_min", text="Min")
                        col.prop(kb, "slider_max", text="Max")
        
                        col = split.column(align=True)
                        col.active = enable_edit_value
                        col.label(text="Blend:")
                        col.prop_search(kb, "vertex_group", obj, "vertex_groups", text="")
                        col.prop_search(kb, "relative_key", key, "key_blocks", text="")
        
                else:
                    box.prop(kb, "interpolation")
                    row = box.column()
                    row.active = enable_edit_value
                    row.prop(key, "eval_time")
        else:
            row.operator("object.shape_key_add", icon='ADD', text="Add Shape ").from_mix = False        

    def draw_camera_background_images(self,layout,obj):
        pass

    def draw_camera_properties(self,layout,obj):

        view = bpy.context.space_data
            
        cam = obj.data

        layout.prop(view, "lock_camera")

        box = layout.box()
        box.label(text="Lens Settings:")
        row = box.row()
        row.prop(cam, "type",expand=True)

        # col = layout.column()

        if cam.type == 'PERSP':
            row = box.row(align=True)
            row.prop(cam, "lens_unit",text="Size")
            if cam.lens_unit == 'MILLIMETERS':
                row.prop(cam, "lens",text="Length")
            elif cam.lens_unit == 'FOV':
                row.prop(cam, "angle",text="Angle")

        elif cam.type == 'ORTHO':
            row = box.row()
            row.label(text="Scale:")
            row.prop(cam, "ortho_scale",text="")

        elif cam.type == 'PANO':
            engine = bpy.context.scene.render.engine
            if engine == 'CYCLES':
                ccam = cam.cycles
                box.prop(ccam, "panorama_type")
                box.prop(cam, "lens_unit")
                if ccam.panorama_type == 'FISHEYE_EQUIDISTANT':
                    box.prop(ccam, "fisheye_fov")
                elif ccam.panorama_type == 'FISHEYE_EQUISOLID':
                    box.prop(ccam, "fisheye_lens", text="Lens")
                    box.prop(ccam, "fisheye_fov")
                elif ccam.panorama_type == 'EQUIRECTANGULAR':
                    sub = box.column(align=True)
                    sub.prop(ccam, "latitude_min", text="Latitude Min")
                    sub.prop(ccam, "latitude_max", text="Max")
                    sub = box.column(align=True)
                    sub.prop(ccam, "longitude_min", text="Longitude Min")
                    sub.prop(ccam, "longitude_max", text="Max")
            elif engine in {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}:
                if cam.lens_unit == 'MILLIMETERS':
                    box.prop(cam, "lens")
                elif cam.lens_unit == 'FOV':
                    box.prop(cam, "angle")

        col = box.column()

        row = col.row(align=True)
        row.label(text="Shift:")
        row.prop(cam, "shift_x", text="X")
        row.prop(cam, "shift_y", text="Y")

        row = col.row(align=True)
        row.label(text="Clip:")
        row.prop(cam, "clip_start", text="Start")
        row.prop(cam, "clip_end", text="End")

        #DOF
        box = layout.box()
        box.label(text="Depth of Field")
        row = box.row()
        row.label(text="Focus on Object:")
        row.prop(cam, "dof_object", text="")

        sub = box.column()
        sub.active = (cam.dof_object is None)
        row = sub.row()
        row.label(text="Focus Distance:")        
        row.prop(cam, "dof_distance", text="")

        dof_options = cam.gpu_dof

        flow = box.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)

        col = flow.column()
        col.prop(dof_options, "fstop")
        col.prop(dof_options, "blades")

        col = flow.column()
        col.prop(dof_options, "rotation")
        col.prop(dof_options, "ratio")        

    def draw_light_properties(self,layout,obj):
        light = obj.data

        box = layout.box()

        row = box.row()
        row.prop(light, "type",expand=True)
        row = box.row()
        row.label(text="Color")
        row.prop(light, "color",text="")
        row = box.row()
        row.label(text="Energy")
        row.prop(light, "energy",text="")
        row = box.row()
        row.label(text="Specular")
        row.prop(light, "specular_factor", text="")
        row = box.row()
        row.prop(light, "use_custom_distance", text="Use Custom Distance")
        if light.use_custom_distance:
            row.prop(light,"cutoff_distance",text="Distance")

        if light.type in {'POINT', 'SPOT', 'SUN'}:
            row = box.row()
            row.label(text="Radius")            
            row.prop(light, "shadow_soft_size", text="")
        elif light.type == 'AREA':
            box = layout.box()
            row = box.row()
            row.label(text="Shape:")
            row.prop(light, "shape",expand=True)

            sub = box.column(align=True)

            if light.shape in {'SQUARE', 'DISK'}:
                row = sub.row(align=True)
                row.label(text="Size:")     
                row.prop(light, "size",text="")
            elif light.shape in {'RECTANGLE', 'ELLIPSE'}:
                row = sub.row(align=True)
                row.label(text="Size:")

                row.prop(light, "size", text="X")
                row.prop(light, "size_y", text="Y")
        
        if light.type == 'SPOT':
            box = layout.box()
            row = box.row()        
            row.label(text="Spot Size:")    
            row.prop(light, "spot_size", text="")
            row = box.row()        
            row.label(text="Spot Blend:")                
            row.prop(light, "spot_blend", text="", slider=True)

            box.prop(light, "show_cone")            

        box = layout.box()
        box.prop(light, "use_shadow", text="Use Shadows")
        box.active = light.use_shadow

        col = box.column()
        row = col.row(align=True)
        row.label(text="Clip:")
        row.prop(light, "shadow_buffer_clip_start", text="Start")
        if light.type == 'SUN':
            row.prop(light, "shadow_buffer_clip_end", text="End")

        row = col.row(align=True)
        row.label(text="Softness:")
        row.prop(light, "shadow_buffer_soft", text="")

        col.separator()

        row = col.row(align=True)
        row.label(text="Bias:")
        row.prop(light, "shadow_buffer_bias", text="")
        row = col.row(align=True)
        row.label(text="Bleed Bias:")        
        row.prop(light, "shadow_buffer_bleed_bias", text="")        
        row = col.row(align=True)
        row.label(text="Exponent:")        
        row.prop(light, "shadow_buffer_exp", text="")

        col.separator()

        col.prop(light, "use_contact_shadow", text="Use Contact Shadows")
        if light.use_shadow and light.use_contact_shadow:
            col = box.column()
            row = col.row(align=True)
            row.label(text="Distance:")  
            row.prop(light, "contact_shadow_distance", text="")
            row = col.row(align=True)
            row.label(text="Softness:")  
            row.prop(light, "contact_shadow_soft_size", text="")
            row = col.row(align=True)
            row.label(text="Bias:")          
            row.prop(light, "contact_shadow_bias", text="")
            row = col.row(align=True)
            row.label(text="Thickness:")          
            row.prop(light, "contact_shadow_thickness", text="")

        if light.type == 'SUN' and light.use_shadow:
            box = layout.box()
            box.label(text="Sun Shadow Settings")
            row = box.row(align=True)
            row.label(text="Cascade Count:")                
            row.prop(light, "shadow_cascade_count", text="")
            row = box.row(align=True)
            row.label(text="Fade:")                 
            row.prop(light, "shadow_cascade_fade", text="")

            row = box.row(align=True)
            row.label(text="Max Distance:")      
            row.prop(light, "shadow_cascade_max_distance", text="")
            row = box.row(align=True)
            row.label(text="Distribution:")                  
            row.prop(light, "shadow_cascade_exponent", text="")

    def draw_empty_properties(self,layout,obj):
        layout.prop(obj, "empty_display_type", text="Display As")

        if obj.empty_display_type == 'IMAGE':
            layout.template_ID(obj, "data", open="image.open", unlink="object.unlink_data")
            layout.template_image(obj, "data", obj.image_user, compact=True)

            layout.row(align=True).row(align=True)

            layout.prop(obj, "use_empty_image_alpha")

            col = layout.column()
            col.active = obj.use_empty_image_alpha
            col.prop(obj, "color", text="Transparency", index=3, slider=True)

            col = layout.column(align=True)
            col.prop(obj, "empty_image_offset", text="Offset X", index=0)
            col.prop(obj, "empty_image_offset", text="Y", index=1)

            col = layout.column()
            col.row().prop(obj, "empty_image_depth", text="Depth", expand=True)
            col.row().prop(obj, "empty_image_side", text="Side", expand=True)
            col.prop(obj, "show_empty_image_orthographic", text="Display Orthographic")
            col.prop(obj, "show_empty_image_perspective", text="Display Perspective")

    def draw_curve_properties(self,layout,obj):
        pass
        #SHAPE, GEO, BEVEL, ACTIVE SPLINE   
        #PATH ANIMATION

    def draw_gpencil_properties(self,layout,obj):
        pass
        #LAYERS

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if obj.type == 'MESH':
            self.draw_uv_maps(layout,obj)
            self.draw_vertex_groups(layout,obj)
            self.draw_shape_keys(layout,obj)
        if obj.type == 'CURVE':
            self.draw_curve_properties(layout,obj)
            self.draw_shape_keys(layout,obj)
        if obj.type == 'FONT':
            pass
        if obj.type == 'EMPTY':
            self.draw_empty_properties(layout,obj)
        if obj.type == 'LATTICE':
            pass
        if obj.type == 'META':
            pass                                         
        if obj.type == 'LIGHT':
            self.draw_light_properties(layout,obj)
        if obj.type == 'CAMERA':
            self.draw_camera_properties(layout,obj)
            self.draw_camera_background_images(layout,obj)
        if obj.type == 'SURFACE':
            pass
        if obj.type == 'ARMATURE':
            pass
        if obj.type == 'SPEAKER':
            pass
        if obj.type == 'FORCE_FIELD':
            pass
        if obj.type == 'GPENCIL':
            pass 
        if obj.type == 'LIGHT_PROBE':
            pass

class VIEW3D_PT_object_drivers(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Object"
    bl_label = "Drivers"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if context.object:
            return True
        else:
            return False

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="",icon='AUTO')

    def draw_driver_expression(self,layout,driver):
        row = layout.row(align=True)
        # row.prop(driver.driver,'show_debug_info',text="",icon='DECORATE')
        if driver.driver.is_valid:
            row.prop(driver.driver,"expression",text="",expand=True,icon='DECORATE')
            if driver.mute:
                row.prop(driver,"mute",text="",icon='DECORATE')
            else:
                row.prop(driver,"mute",text="",icon='DECORATE')
        else:
            row.prop(driver.driver,"expression",text="",expand=True,icon='ERROR')
            if driver.mute:
                row.prop(driver,"mute",text="",icon='DECORATE')
            else:
                row.prop(driver,"mute",text="",icon='DECORATE')

    def draw_driver_variable(self,layout,driver,object_name):
        for var in driver.driver.variables:
            col = layout.column()
            boxvar = col.box()
            row = boxvar.row(align=True)
            row.prop(var,"name",text="",icon='FORWARD')
            
            props = row.operator("bp_driver.remove_variable",text="",icon='X',emboss=False)
            props.object_name = object_name
            props.data_path = driver.data_path
            props.array_index = driver.array_index
            props.var_name = var.name
            for target in var.targets:
                # if driver.driver.show_debug_info:
                row = boxvar.row()
                row.prop(var,"type",text="")
                row = boxvar.row()
                row.prop(target,"id",text="")
                row = boxvar.row(align=True)
                row.prop(target,"data_path",text="",icon='ANIM_DATA')
                if target.id and target.data_path != "":
                    value = eval('bpy.data.objects["' + target.id.name + '"]'"." + target.data_path)
                else:
                    value = "ERROR#"
                row = boxvar.row()
                row.label(text="",icon='BLANK1')
                row.label(text="",icon='BLANK1')
                if type(value).__name__ == 'str':
                    row.label(text="Value: " + value)
                elif type(value).__name__ == 'float':
                    row.label(text="Value: " + str(value))
                elif type(value).__name__ == 'int':
                    row.label(text="Value: " + str(value))
                elif type(value).__name__ == 'bool':
                    row.label(text="Value: " + str(value))       

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if obj:
            if not obj.animation_data:
                layout.label(text="There are no drivers assigned to the object",icon='ERROR')
            else:
                if len(obj.animation_data.drivers) == 0:
                    layout.label(text="There are no drivers assigned to the object",icon='ERROR')
                for driver in obj.animation_data.drivers:
                    box = layout.box()
                    row = box.row()
                    driver_name = driver.data_path
                    if driver_name in {"location","rotation_euler","dimensions" ,"lock_scale",'lock_location','lock_rotation'}:
                        if driver.array_index == 0:
                            driver_name = driver_name + " X"
                        if driver.array_index == 1:
                            driver_name = driver_name + " Y"
                        if driver.array_index == 2:
                            driver_name = driver_name + " Z"    
                    value = eval('bpy.data.objects["' + obj.name + '"].' + driver.data_path)
                    if type(value).__name__ == 'str':
                        row.label(text=driver_name + " = " + str(value),icon='AUTO')
                    elif type(value).__name__ == 'float':
                        row.label(text=driver_name + " = " + str(value),icon='AUTO')
                    elif type(value).__name__ == 'int':
                        row.label(text=driver_name + " = " + str(value),icon='AUTO')
                    elif type(value).__name__ == 'bool':
                        row.label(text=driver_name + " = " + str(value),icon='AUTO')
                    elif type(value).__name__ == 'bpy_prop_array':
                        row.label(text=driver_name + " = " + str(value[driver.array_index]),icon='AUTO')
                    elif type(value).__name__ == 'Vector':
                        row.label(text=driver_name + " = " + str(value[driver.array_index]),icon='AUTO')
                    elif type(value).__name__ == 'Euler':
                        row.label(text=driver_name + " = " + str(value[driver.array_index]),icon='AUTO')
                    else:
                        row.label(text=driver_name + " = " + str(type(value)),icon='AUTO')

                    coll = bp_utils.get_assembly_collection(obj)
                    if coll:
                        assembly = bp_types.Assembly(coll)
                        props = row.operator('bp_driver.get_vars_from_object',text="",icon='DRIVER')
                        props.object_name = obj.name
                        props.var_object_name = assembly.obj_prompts.name
                        props.data_path = driver.data_path
                        props.array_index = driver.array_index    
                    self.draw_driver_expression(box,driver)
                    self.draw_driver_variable(box,driver,obj.name)                    

class VIEW3D_PT_grease_pencil(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Object"
    bl_label = "Grease Pencil Layers"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if context.object:
            if context.object.type == 'GPENCIL':
                return True
            else:
                return False
        else:
            return False

    def draw_header(self, context):
        layout = self.layout
        obj = context.object
        layout.label(text="",icon='COLOR')

    def draw(self, context):
        layout = self.layout
        props = layout.operator("bp_general.split_region")
        props.space_type = 'DOPESHEET_EDITOR'
        props.space_sub_type = 'GPENCIL'
        props.split_direction = 'HORIZONTAL'
        props.split_factor = .2
        

class VIEW3D_MT_bp_add(bpy.types.Menu):
    bl_label = "Add"

    def draw(self, context):
        layout = self.layout

        # note, don't use 'EXEC_SCREEN' or operators won't get the 'v3d' context.

        # Note: was EXEC_AREA, but this context does not have the 'rv3d', which prevents
        #       "align_view" to work on first call (see [#32719]).
        # layout.operator_context = 'EXEC_REGION_WIN'

        # layout.operator_menu_enum("object.mesh_add", "type", text="Mesh", icon='OUTLINER_OB_MESH')
        layout.menu("VIEW3D_MT_mesh_add", icon='OUTLINER_OB_MESH')

        # layout.operator_menu_enum("object.curve_add", "type", text="Curve", icon='OUTLINER_OB_CURVE')
        layout.menu("VIEW3D_MT_curve_add", icon='OUTLINER_OB_CURVE')
        # layout.operator_menu_enum("object.surface_add", "type", text="Surface", icon='OUTLINER_OB_SURFACE')
        layout.menu("VIEW3D_MT_surface_add", icon='OUTLINER_OB_SURFACE')
        layout.menu("VIEW3D_MT_metaball_add", text="Metaball", icon='OUTLINER_OB_META')
        layout.operator("bp_object.add_text_dialog", text="Text", icon='OUTLINER_OB_FONT')
        layout.operator_menu_enum("object.gpencil_add", "type", text="Grease Pencil", icon='OUTLINER_OB_GREASEPENCIL')

        layout.separator()

        if bpy.types.VIEW3D_MT_armature_add.is_extended():
            layout.menu("VIEW3D_MT_armature_add", icon='OUTLINER_OB_ARMATURE')
        else:
            layout.operator("object.armature_add", text="Armature", icon='OUTLINER_OB_ARMATURE')

        layout.operator("object.add", text="Lattice", icon='OUTLINER_OB_LATTICE').type = 'LATTICE'

        layout.separator()

        layout.operator_menu_enum("object.empty_add", "type", text="Empty", icon='OUTLINER_OB_EMPTY')
        layout.menu("VIEW3D_MT_image_add", text="Image", icon='OUTLINER_OB_IMAGE')

        layout.separator()

        layout.menu("VIEW3D_MT_light_add", icon='OUTLINER_OB_LIGHT')
        layout.menu("VIEW3D_MT_lightprobe_add", icon='OUTLINER_OB_LIGHTPROBE')

        layout.separator()

        if bpy.types.VIEW3D_MT_camera_add.is_extended():
            layout.menu("VIEW3D_MT_camera_add", icon='OUTLINER_OB_CAMERA')
        else:
            layout.operator("bp_object.add_camera", text="Camera", icon='OUTLINER_OB_CAMERA')
            
            # bpy.types.VIEW3D_MT_camera_add.draw(self, context)

        layout.separator()

        layout.operator("object.speaker_add", text="Speaker", icon='OUTLINER_OB_SPEAKER')

        layout.separator()

        layout.operator_menu_enum("object.effector_add", "type", text="Force Field", icon='OUTLINER_OB_FORCE_FIELD')

        layout.separator()

        has_collections = bool(bpy.data.collections)
        col = layout.column()
        col.enabled = has_collections

        if not has_collections or len(bpy.data.collections) > 10:
            col.operator_context = 'INVOKE_REGION_WIN'
            col.operator(
                "object.collection_instance_add",
                text="Collection Instance..." if has_collections else "No Collections to Instance",
                icon='OUTLINER_OB_GROUP_INSTANCE',
            )
        else:
            col.operator_menu_enum(
                "object.collection_instance_add",
                "collection",
                text="Collection Instance",
                icon='OUTLINER_OB_GROUP_INSTANCE',
            )

classes = (
    VIEW3D_PT_objects,
    VIEW3D_PT_object_selection,
    SCENE_UL_objects,
    VIEW3D_PT_object_transform,
    VIEW3D_PT_object_data,
    VIEW3D_PT_object_view_options,
    VIEW3D_PT_object_material,
    VIEW3D_PT_object_modifiers,
    VIEW3D_PT_object_constraints,
    VIEW3D_PT_object_drivers,
    VIEW3D_PT_grease_pencil,
    VIEW3D_MT_bp_add
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
