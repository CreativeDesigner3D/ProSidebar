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
from .. import sidebar_utils

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
        
        layout.operator('bp_object.update_dependencies')

        # layout.operator('bp_object.set_base_point')
        
        if obj:
            self.draw_modes(obj,layout)
            row = layout.row(align=True)
            row.scale_y = 1.3
            split = row.split(factor=.7,align=True)
            split.popover(panel="VIEW3D_PT_object_selection",text=obj.name,icon=sidebar_utils.get_object_icon(obj))
            split.menu("VIEW3D_MT_bp_add", text="Add",icon='ADD')
            layout.prop(obj,'name')
            layout.prop(obj,'parent')
        else:
            row = layout.row(align=True)
            row.scale_y = 1.3
            split = row.split(factor=.7,align=True)
            split.popover(panel="VIEW3D_PT_object_selection",text="No Selection",icon='DOT')
            split.menu("VIEW3D_MT_bp_add", text="Add",icon='ADD')


class SCENE_UL_objects(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name,icon=sidebar_utils.get_object_icon(item))
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
            if obj.scale.x != 1 or obj.scale.y != 1 or obj.scale.z != 1:
                props = layout.operator('object.transform_apply',text="Apply Scale",icon='ERROR')
                props.location = False
                props.rotation = False
                props.scale = True

            col = layout.column(align=True)
            col.label(text='Dimensions:')
            #X
            row = col.row(align=True)
            row.prop(obj,"lock_scale",index=0,text="")
            if obj.lock_scale[0]:
                row.label(text="X: " + str(round(sidebar_utils.meter_to_active_unit(obj.dimensions.x),4)))
            else:
                row.prop(obj,"dimensions",index=0,text="X")
            #Y
            row = col.row(align=True)
            row.prop(obj,"lock_scale",index=1,text="")
            if obj.lock_scale[1]:
                row.label(text="Y: " + str(round(sidebar_utils.meter_to_active_unit(obj.dimensions.y),4)))
            else:
                row.prop(obj,"dimensions",index=1,text="Y")
            #Z
            row = col.row(align=True)
            row.prop(obj,"lock_scale",index=2,text="")
            if obj.lock_scale[2]:
                row.label(text="Z: " + str(round(sidebar_utils.meter_to_active_unit(obj.dimensions.z),4)))
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
            row.label(text="X: " + str(round(sidebar_utils.meter_to_active_unit(obj.location.x),4)))
        else:
            row.prop(obj,"location",index=0,text="X")
        #Y    
        row = col.row(align=True)
        row.prop(obj,"lock_location",index=1,text="")
        if obj.lock_location[1]:
            row.label(text="Y: " + str(round(sidebar_utils.meter_to_active_unit(obj.location.y),4)))
        else:
            row.prop(obj,"location",index=1,text="Y")
        #Z    
        row = col.row(align=True)
        row.prop(obj,"lock_location",index=2,text="")
        if obj.lock_location[2]:
            row.label(text="Z: " + str(round(sidebar_utils.meter_to_active_unit(obj.location.z),4)))
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
        layout.label(text='',icon=sidebar_utils.get_object_icon(context.object))

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
            # else:
            #     box.operator("bp_assembly.connect_meshes_to_hooks_in_assembly", text="Connect Mesh Hooks").obj_name = obj.name
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

        box = layout.box()
        box.prop(view, "lock_camera")

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
        box.prop(cam.dof,'use_dof',text="Depth of Field")
        if cam.dof.use_dof:
            row = box.row()
            row.label(text="Focus on Object:")
            row.prop(cam.dof, "focus_object", text="")

            sub = box.column()
            sub.active = (cam.dof.focus_object is None)
            row = sub.row()
            row.label(text="Focus Distance:")        
            row.prop(cam.dof, "focus_distance", text="")

            flow = box.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)

            col = flow.column()
            col.prop(cam.dof, "aperture_fstop")
            col.prop(cam.dof, "aperture_blades")

            col = flow.column()
            col.prop(cam.dof, "aperture_rotation")
            col.prop(cam.dof, "aperture_ratio")

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

    def draw_text_properties(self,layout,obj):
        curve = obj.data

        box = layout.box()
        box.label(text="Font Selection")
        row = box.split(factor=0.25)
        row.label(text="Font")
        row.template_ID(curve, "font", open="font.open", unlink="font.unlink") 

        if len(bpy.context.selected_objects) > 1:
            box.operator('bp_object.update_selected_text_with_active_font',text="Change Selected Text to - " + curve.font.name,icon='FILE_REFRESH')    

        box = layout.box()
        box.label(text="Alignment and Spacing")
        col = box.column()
        col.prop(curve, "align_x", text="Horizontal")
        col.prop(curve, "align_y", text="Vertical")

        row = box.row(align=True)
        row.label(text="Offset")
        row.prop(curve, "offset_x", text="X")
        row.prop(curve, "offset_y", text="Y")

        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="Character Spacing")
        row.prop(curve, "space_character", text="")
        row = col.row(align=True)
        row.label(text="Word Spacing")        
        row.prop(curve, "space_word", text="")
        row = col.row(align=True)
        row.label(text="Line Spacing")        
        row.prop(curve, "space_line", text="")

        box = layout.box()
        box.label(text="Geometry")    
        row = box.row()
        row.label(text="Extrude")    
        row.prop(curve, "extrude",text="")
        row = box.row()
        row.label(text="Offset")           
        row.prop(curve, "offset",text="")
        
        row = box.row(align=True)
        row.label(text="Bevel")
        row.prop(curve, "bevel_depth", text="Depth")
        row.prop(curve, "bevel_resolution", text="Resolution")

        row = box.split(factor=0.5)
        row.label(text="Taper Object")
        row.prop(curve, "taper_object",text="")

        row = box.split(factor=0.5)
        row.label(text="Bevel Object")        
        row.prop(curve, "bevel_object", text="")

        if curve.bevel_object is not None:
            row = box.row()
            row.alignment = 'RIGHT'
            row.prop(curve, "use_fill_caps")

        row = box.row()
        row.label(text="Fill Mode")
        row.prop(curve, "fill_mode",expand=True)
        row = box.row()
        row.alignment = 'RIGHT'
        row.prop(curve, "use_fill_deform")

    def draw_curve_properties(self,layout,obj):
        curve = obj.data

        is_surf = type(curve) is bpy.types.SurfaceCurve
        is_curve = type(curve) is bpy.types.Curve
        is_text = type(curve) is bpy.types.TextCurve

        box = layout.box()
        box.label(text="Curve Settings")
        if is_curve:
            row = box.row()
            row.label(text="Type")
            row.prop(curve, "dimensions", expand=True)

        row = box.row(align=True)
        row.label(text="Resolution")
        row.prop(curve, "resolution_u", text="Preview")
        row.prop(curve, "render_resolution_u", text="Render")

        if is_surf:
            row = box.row(align=True)
            row.label(text="Resolution V")
            row.prop(curve, "resolution_v", text="Preview")
            row.prop(curve, "render_resolution_v", text="Render")
            return #DON'T DRAW ANY MORE PROPERTIES FOR SURFACE TYPE

        if is_curve and curve.dimensions == '3D':
            row = box.row(align=True)
            row.label(text="Twist")
            row.prop(curve, "twist_mode",text="")
            row.prop(curve, "twist_smooth", text="Smooth")

        box = layout.box()
        box.label(text="Geometry")    
        row = box.row()
        row.label(text="Extrude")    
        row.prop(curve, "extrude",text="")
        row = box.row()
        row.label(text="Offset")           
        row.prop(curve, "offset",text="")
        
        row = box.row(align=True)
        row.label(text="Bevel")
        row.prop(curve, "bevel_depth", text="Depth")
        row.prop(curve, "bevel_resolution", text="Resolution")

        row = box.row(align=True)
        row.label(text="Start/End")
        row.prop(curve, "bevel_factor_start", text="Start")
        row.prop(curve, "bevel_factor_end", text="End")

        row = box.split(factor=0.5)
        row.label(text="Taper Object")
        row.prop(curve, "taper_object",text="")

        row = box.split(factor=0.5)
        row.label(text="Bevel Object")        
        row.prop(curve, "bevel_object", text="")

        if curve.bevel_object is not None:
            row = box.row()
            row.alignment = 'RIGHT'
            row.prop(curve, "use_fill_caps")

        row = box.row()
        row.label(text="Fill Mode")
        row.prop(curve, "fill_mode",expand=True)
        row = box.row()
        row.alignment = 'RIGHT'
        row.prop(curve, "use_fill_deform")


        act_spline = curve.splines.active
        box = layout.box()
        box.label(text="Active Spline")
        row = box.row()
        row.prop(act_spline, "use_cyclic_u")
        row.prop(act_spline, "use_smooth")

    def draw_gpencil_vertex_groups(self,layout,obj):
        group = obj.vertex_groups.active

        rows = 2
        if group:
            rows = 4

        box = layout.box()
        row = box.row()
        row.label(text="Vertex Groups:", icon='GROUP_VERTEX')
        if len(obj.vertex_groups) > 0:
            row = box.row()
            row.template_list("GPENCIL_UL_vgroups", "", obj, "vertex_groups", obj.vertex_groups, "active_index", rows=rows)

            col = row.column(align=True)
            col.operator("object.vertex_group_add", icon='ADD', text="")
            col.operator("object.vertex_group_remove", icon='REMOVE', text="").all = False
            # col.menu("MESH_MT_vertex_group_context_menu", icon='DOWNARROW_HLT', text="")
            col.menu("GPENCIL_MT_gpencil_vertex_group", icon='DOWNARROW_HLT', text="")
            if group:
                col.separator()
                col.operator("object.vertex_group_move", icon='TRIA_UP', text="").direction = 'UP'
                col.operator("object.vertex_group_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

            if obj.vertex_groups and (obj.mode == 'EDIT_GPENCIL' or 'SCULPT_GPENCIL'):
                row = box.row()

                sub = row.row(align=True)
                sub.operator("gpencil.vertex_group_assign", text="Assign")
                sub.operator("gpencil.vertex_group_remove_from", text="Remove")

                sub = row.row(align=True)
                sub.operator("gpencil.vertex_group_select", text="Select")
                sub.operator("gpencil.vertex_group_deselect", text="Deselect")

                box.prop(bpy.context.tool_settings, "vertex_group_weight", text="Weight")

        else:
            row.operator('object.vertex_group_add', icon='ADD', text="Add")

    def draw_gpencil_layers(self,layout,obj):
        gpd = obj.data

        if (gpd is None) or (not gpd.layers):
            layout.operator("gpencil.layer_add", text="New Layer")
        else:
            gpl = gpd.layers.active

            layer_rows = 7

            box = layout.box()
            row = box.row()
            row.label(text="Layers:", icon='NONE')
            row = box.row()

            row.template_list("GPENCIL_UL_layer", "", gpd, "layers", gpd.layers, "active_index",
                              rows=layer_rows, sort_reverse=True, sort_lock=True)

            col = row.column()
            sub = col.column(align=True)
            sub.operator("gpencil.layer_add", icon='ADD', text="")
            sub.operator("gpencil.layer_remove", icon='REMOVE', text="")

            if gpl:
                sub.menu("GPENCIL_MT_layer_context_menu", icon='DOWNARROW_HLT', text="")

                if len(gpd.layers) > 1:
                    col.separator()

                    sub = col.column(align=True)
                    sub.operator("gpencil.layer_move", icon='TRIA_UP', text="").type = 'UP'
                    sub.operator("gpencil.layer_move", icon='TRIA_DOWN', text="").type = 'DOWN'

                    col.separator()

                    sub = col.column(align=True)
                    sub.operator("gpencil.layer_isolate", icon='LOCKED', text="").affect_visibility = False
                    sub.operator("gpencil.layer_isolate", icon='RESTRICT_VIEW_ON', text="").affect_visibility = True

            # Layer main properties
            row = box.row(align=True)

            if gpl:
                row.prop(gpl, "blend_mode", text="Blend")
                row.prop(gpl, "opacity", text="Opacity", slider=True)

    def draw_metaball_properties(self,layout,obj):
        mball = obj.data

        col = layout.column(align=True)
        col.prop(mball, "resolution", text="Resolution Viewport")
        col.prop(mball, "render_resolution", text="Render")

        col.separator()

        col.prop(mball, "threshold", text="Influence Threshold")

        col.separator()

        col.prop(mball, "update_method", text="Update on Edit")

        if obj.mode == 'EDIT':
            col = layout.column()
            metaelem = mball.elements.active    

            col.prop(metaelem, "type")

            col.separator()

            col.prop(metaelem, "stiffness", text="Stiffness")
            col.prop(metaelem, "radius", text="Radius")
            col.prop(metaelem, "use_negative", text="Negative")
            col.prop(metaelem, "hide", text="Hide")

            sub = col.column(align=True)

            if metaelem.type in {'CUBE', 'ELLIPSOID'}:
                sub.prop(metaelem, "size_x", text="Size X")
                sub.prop(metaelem, "size_y", text="Y")
                sub.prop(metaelem, "size_z", text="Z")

            elif metaelem.type == 'CAPSULE':
                sub.prop(metaelem, "size_x", text="Size X")

            elif metaelem.type == 'PLANE':
                sub.prop(metaelem, "size_x", text="Size X")
                sub.prop(metaelem, "size_y", text="Y")

    def draw_lattice_properties(self,layout,obj):
        lat = obj.data

        col = layout.column()

        sub = col.column(align=True)
        sub.prop(lat, "points_u", text="Resolution U")
        sub.prop(lat, "points_v", text="V")
        sub.prop(lat, "points_w", text="W")

        col.separator()

        sub = col.column(align=True)
        sub.prop(lat, "interpolation_type_u", text="Interpolation U")
        sub.prop(lat, "interpolation_type_v", text="V")
        sub.prop(lat, "interpolation_type_w", text="W")

        col.separator()

        col.prop(lat, "use_outside")

        col.separator()

        col.prop_search(lat, "vertex_group", obj, "vertex_groups")

    def draw_light_probe_properties(self,layout,obj):
        probe = obj.data

        if probe.type == 'GRID':
            col = layout.column()
            col.prop(probe, "influence_distance", text="Distance")
            col.prop(probe, "falloff")
            col.prop(probe, "intensity")

            sub = col.column(align=True)
            sub.prop(probe, "grid_resolution_x", text="Resolution X")
            sub.prop(probe, "grid_resolution_y", text="Y")
            sub.prop(probe, "grid_resolution_z", text="Z")

        elif probe.type == 'PLANAR':
            col = layout.column()
            col.prop(probe, "influence_distance", text="Distance")
            col.prop(probe, "falloff")
        else:
            col = layout.column()
            col.prop(probe, "influence_type")

            if probe.influence_type == 'ELIPSOID':
                col.prop(probe, "influence_distance", text="Radius")
            else:
                col.prop(probe, "influence_distance", text="Size")

            col.prop(probe, "falloff")
            col.prop(probe, "intensity")

        sub = col.column(align=True)
        if probe.type != 'PLANAR':
            sub.prop(probe, "clip_start", text="Clipping Start")
        else:
            sub.prop(probe, "clip_start", text="Clipping Offset")

        if probe.type != 'PLANAR':
            sub.prop(probe, "clip_end", text="End")        

        if probe.type == 'GRID':
            col.prop(probe, "visibility_buffer_bias", text="Bias")
            col.prop(probe, "visibility_bleed_bias", text="Bleed Bias")
            col.prop(probe, "visibility_blur", text="Blur")

        row = col.row(align=True)
        row.prop(probe, "visibility_collection")
        row.prop(probe, "invert_visibility_collection", text="", icon='ARROW_LEFTRIGHT')

        layout.prop(probe, "use_custom_parallax")

        col = layout.column()
        col.active = probe.use_custom_parallax

        col.prop(probe, "parallax_type")

        if probe.parallax_type == 'ELIPSOID':
            col.prop(probe, "parallax_distance", text="Radius")
        else:
            col.prop(probe, "parallax_distance", text="Size")

        if probe.type == 'PLANAR':
            col.prop(obj, "empty_display_size", text="Arrow Size")
            col.prop(probe, "show_data")

        if probe.type in {'GRID', 'CUBEMAP'}:
            col.prop(probe, "show_influence")
            col.prop(probe, "show_clip")

        if probe.type == 'CUBEMAP':
            sub = col.column()
            sub.active = probe.use_custom_parallax
            sub.prop(probe, "show_parallax")

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
            self.draw_text_properties(layout,obj)
        if obj.type == 'EMPTY':
            self.draw_empty_properties(layout,obj)
        if obj.type == 'LATTICE':
            self.draw_lattice_properties(layout,obj)
        if obj.type == 'META':
            self.draw_metaball_properties(layout,obj)                              
        if obj.type == 'LIGHT':
            self.draw_light_properties(layout,obj)
        if obj.type == 'CAMERA':
            self.draw_camera_properties(layout,obj)
            self.draw_camera_background_images(layout,obj)
        if obj.type == 'SURFACE':
            self.draw_curve_properties(layout,obj)
        if obj.type == 'ARMATURE':
            pass #TODO:
        if obj.type == 'SPEAKER':
            pass #TODO
        if obj.type == 'FORCE_FIELD':
            pass #TODO
        if obj.type == 'GPENCIL':
            self.draw_gpencil_vertex_groups(layout,obj)
            self.draw_gpencil_layers(layout,obj)
        if obj.type == 'LIGHT_PROBE':
            self.draw_light_probe_properties(layout,obj)             
        
class VIEW3D_PT_camera_background_image(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Background Images"
    bl_category = "Object"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}

    @classmethod
    def poll(cls, context):
        if context.object and context.object.type == 'CAMERA':
            return True
        else:
            return False

    def draw_header(self, context):
        if context.active_object is not None:
            if context.object.type == 'CAMERA':
                cam = context.object.data
                self.layout.prop(cam, "show_background_images", text="")

    def draw(self, context):
        if context.active_object is not None:
            if context.object.type == 'CAMERA':
                layout = self.layout
                layout.use_property_split = True
                layout.use_property_decorate = False

                cam = context.object.data
                use_multiview = context.scene.render.use_multiview

                col = layout.column(align=True)
                row = col.row()
                row.operator("view3d.background_image_add", text="Add Image")
                row.operator('bp_object.collapse_all_background_images', text="", icon='FULLSCREEN_EXIT')

                for i, bg in enumerate(cam.background_images):
                    layout.active = cam.show_background_images
                    box = layout.box()
                    row = box.row(align=True)
                    row.prop(bg, "show_expanded", text="", emboss=False)
                    if bg.source == 'IMAGE' and bg.image:
                        row.prop(bg.image, "name", text="", emboss=False)
                    elif bg.source == 'MOVIE_CLIP' and bg.clip:
                        row.prop(bg.clip, "name", text="", emboss=False)
                    elif bg.source and bg.use_camera_clip:
                        row.label(text="Active Clip")
                    else:
                        row.label(text="Not Set")

                    row.prop(
                        bg,
                        "show_background_image",
                        text="",
                        emboss=False,
                        icon='RESTRICT_VIEW_OFF' if bg.show_background_image else 'RESTRICT_VIEW_ON',
                    )

                    row.operator("bp_object.background_image_remove", text="", icon='X').index = i

                    if bg.show_expanded:
                        row = box.row()
                        row.prop(bg, "source", expand=True)

                        has_bg = False
                        if bg.source == 'IMAGE':
                            row = box.row()
                            row.template_ID(bg, "image", open="image.open")
                            if bg.image is not None:
                                box.template_image(bg, "image", bg.image_user, compact=True)
                                has_bg = True

                                if use_multiview:
                                    box.prop(bg.image, "use_multiview")

                                    column = box.column()
                                    column.active = bg.image.use_multiview

                                    column.label(text="Views Format:")
                                    column.row().prop(bg.image, "views_format", expand=True)

                                    sub = column.box()
                                    sub.active = bg.image.views_format == 'STEREO_3D'
                                    sub.template_image_stereo_3d(bg.image.stereo_3d_format)

                        elif bg.source == 'MOVIE_CLIP':
                            box.prop(bg, "use_camera_clip", text="Active Clip")

                            column = box.column()
                            column.active = not bg.use_camera_clip
                            column.template_ID(bg, "clip", open="clip.open")

                            if bg.clip:
                                column.template_movieclip(bg, "clip", compact=True)

                            if bg.use_camera_clip or bg.clip:
                                has_bg = True

                            column = box.column()
                            column.active = has_bg
                            column.prop(bg.clip_user, "use_render_undistorted")
                            column.prop(bg.clip_user, "proxy_render_size")

                        if has_bg:
                            col = box.column()
                            col.prop(bg, "alpha", slider=True)
                            col.row().prop(bg, "display_depth", expand=True)

                            col.row().prop(bg, "frame_method", expand=True)

                            row = box.row()
                            row.prop(bg, "offset")

                            col = box.column()
                            col.prop(bg, "rotation")
                            col.prop(bg, "scale")

                            col.prop(bg, "use_flip_x")
                            col.prop(bg, "use_flip_y")


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

        layout.separator()

        layout.operator('bp.draw_plane',icon='MATPLANE')
        layout.operator('bp_object.particle_paint',icon='SHADERFX')   
        layout.operator('bp_object.place_area_lamp',icon='LIGHT_AREA')   


classes = (
    VIEW3D_PT_objects,
    VIEW3D_PT_object_selection,
    SCENE_UL_objects,
    VIEW3D_PT_object_transform,
    VIEW3D_PT_object_data,
    VIEW3D_PT_object_view_options,
    VIEW3D_PT_object_modifiers,
    VIEW3D_PT_object_constraints,
    VIEW3D_MT_bp_add,
    VIEW3D_PT_camera_background_image
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
