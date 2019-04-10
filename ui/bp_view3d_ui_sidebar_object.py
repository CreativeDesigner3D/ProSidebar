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
from .modifiers import Modifier
from ..bp_lib import bp_unit, bp_utils

#TODO: IMPLEMENT OBJECT DATA
#TODO: FIGURE OUT HOW TO IMPLEMENT INFO FOR GREASE PENCIL (LAYERS, MATERIALS, ...)
#TODO: IMPLEMENT CONSTRAINTS PANEL

class VIEW3D_PT_objects(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Object"
    bl_category = "Object"
    bl_options = {'HIDE_HEADER'}
    
    @classmethod
    def poll(cls, context):
        return context.object
    
    def draw(self, context):
        obj = context.object
        scene = context.scene
        layout = self.layout
        
        row = layout.row(align=True)
        row.scale_y = 1.3
        split = row.split(factor=.7,align=True)
        split.popover(panel="VIEW3D_PT_object_selection",text=obj.name,icon=bp_utils.get_object_icon(obj))
        split.menu("VIEW3D_MT_add", text="Add",icon='ADD')
        layout.prop(obj,'name')


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
        if obj.type not in {'EMPTY','CAMERA','LAMP'}:
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
        pass


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
            col.menu("MESH_MT_vertex_group_specials", icon='DOWNARROW_HLT', text="")
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
        pass
        #LENS PROPS
        #VIEWPORT PROPS
        #DOF
        
    def draw_light_properties(self,layout,obj):
        pass
        #LIGHT PROPS
        #SHADOW PROPS

    def draw_empty_properties(self,layout,obj):
        pass
        #TYPE, SIZE
        #IMAGE

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

class VIEW3D_PT_object_prompts(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Object"
    bl_label = "Prompts"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if context.object:
            return True
        else:
            return False

    def draw_header(self, context):
        layout = self.layout
        obj = context.object
        layout.label(text="",icon='LINENUMBERS_ON')

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if obj:
            obj.prompt_page.draw_prompts(layout,'OBJECT')

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
    VIEW3D_PT_object_prompts
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
