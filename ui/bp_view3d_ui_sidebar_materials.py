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

class VIEW3D_PT_material_library(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "All Materials"
    bl_category = "Materials"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout    

        row = layout.row(align=True)
        row.scale_y = 1.3
        row.operator("library.add_material_from_library",text="Material Library",icon='DISK_DRIVE')
        row.menu('LIBRARY_MT_material_library',text="",icon="DISCLOSURE_TRI_DOWN")
        row = layout.row(align=True)
        row.scale_y = 1.3
        row.menu('VIEW3D_MT_add_material',text="Add Material",icon="ADD")
        


class VIEW3D_PT_all_materials(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "All Materials"
    bl_category = "Materials"
    # bl_options = {'HIDE_HEADER'}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='',icon='MATERIAL')

    def draw(self, context):
        obj = context.object
        scene = context.scene
        layout = self.layout

        if len(bpy.data.materials) > 0:
            layout.template_list("BP_UL_materials", "", bpy.data, "materials", scene.bp_props, "selected_material_index", rows=4)
            
            if scene.bp_props.selected_material_index <= len(bpy.data.materials):
                mat = bpy.data.materials[scene.bp_props.selected_material_index]
                row = layout.row()
                row.prop(mat,'name')
                row.popover(panel="VIEW3D_PT_material_settings",text="",icon='SETTINGS')

        layout.operator('library.assign_material',text="Assign Selected Material",icon='NONE')

class VIEW3D_PT_object_materials(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Selected Object Materials"
    bl_category = "Materials"
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
            if gpcolor.fill_style == 'TEXTURE' or (gpcolor.use_fill_texture_mix is True and gpcolor.fill_style == 'SOLID'):
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


class BP_UL_materials(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name,icon_value=icon)
        layout.operator('bp_material.delete_material',icon='X',text="",emboss=False).material_name = item.name         


class VIEW3D_MT_add_material(bpy.types.Menu):
    bl_label = "Add Material"

    def draw(self, context):
        layout = self.layout
        layout.operator("material.new",icon='ADD')
        # layout.operator("material.create_principled_material",icon='SMOOTH')
        layout.operator("bp_material.create_material_from_image",icon='FILE_IMAGE')               
        


class VIEW3D_PT_material_settings(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    # bl_region_type = 'UI'    
    bl_label = "Material Settings"
    bl_ui_units_x = 18
    # COMPAT_ENGINES = {'BLENDER_EEVEE'}

    def draw(self, context):
        scene = context.scene
        rd = scene.render

        layout = self.layout

        mat = bpy.data.materials[context.scene.bp_props.selected_material_index]

        if rd.engine == 'BLENDER_EEVEE':
            
            box = layout.box()
            box.label(text="Solid View Settings")
            row = box.row()
            row.label(text="Color")
            row.prop(mat, "diffuse_color", text="")
            row = box.row()
            row.label(text="Metallic")            
            row.prop(mat, "metallic",text="")
            row = box.row()
            row.label(text="Roughness")            
            row.prop(mat, "roughness",text="")


            box = layout.box()
            row = box.row()
            row.label(text="Shadow and Transparency Options")   
            row = box.row()
            row.label(text="Blend Mode")               
            col = box.column(align=True)
            row = col.row(align=True)
            row.prop_enum(mat, "blend_method", 'OPAQUE', text="Opaque") 
            row.prop_enum(mat, "blend_method", 'ADD', text="Additive") 
            row.prop_enum(mat, "blend_method", 'MULTIPLY', text="Multiply")
            row = col.row(align=True) 
            row.prop_enum(mat, "blend_method", 'CLIP', text="Alpha Clip") 
            row.prop_enum(mat, "blend_method", 'HASHED', text="Alpha Hashed") 
            row.prop_enum(mat, "blend_method", 'BLEND', text="Alpha Blend")    

            if mat.blend_method not in {'OPAQUE', 'CLIP', 'HASHED'}:
                box.prop(mat, "show_transparent_back")

            row = box.row()
            row.label(text="Shadow Method")       
            row = box.row()          
            row.prop(mat, "shadow_method",expand=True)

            row = box.row()
            row.active = ((mat.blend_method == 'CLIP') or (mat.shadow_method == 'CLIP'))
            row.prop(mat, "alpha_threshold")

            box.prop(mat, "use_backface_culling") 

            box = layout.box()
            box.label(text="Reflection/Refraction Settings")
            row = box.row()
            row.prop(mat, "use_screen_refraction")
            if mat.use_screen_refraction:
                row.prop(mat, "refraction_depth")
            box.prop(mat, "use_sss_translucency")
            
            box = layout.box()
            box.prop(mat, "pass_index")    

        if rd.engine == 'CYCLES':
            box = layout.box()
            box.label(text="Surface")
            box.prop(mat.cycles, "sample_as_light", text="Multiple Importance")
            box.prop(mat.cycles, "use_transparent_shadow")
            row = box.row()
            row.label("Displacement Method")
            row.prop(mat.cycles, "displacement_method", text="Displacement",expand=True)

            box = layout.box()
            box.label(text="Volume")
            row = box.row()
            row.label(text="Sampling Type")
            row.prop(mat.cycles, "volume_sampling", text="",expand=True)
            row = box.row()
            row.label(text="Interpolation Method")
            row.prop(mat.cycles, "volume_interpolation", text="Interpolation",expand=True)
            box.prop(mat.cycles, "homogeneous_volume", text="Homogeneous")

classes = (
    VIEW3D_PT_material_library,
    VIEW3D_PT_all_materials,
    VIEW3D_PT_object_materials,
    BP_UL_materials,
    VIEW3D_MT_add_material,
    VIEW3D_PT_material_settings
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()        