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

class VIEW3D_PT_view_info(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "View"
    bl_category = "View"
    bl_options = {'HIDE_HEADER'}
    
    def draw(self, context):
        layout = self.layout
        window = context.window
        scene = window.scene        
        row = layout.row(align=True)
        row.scale_y = 1.3
        row.template_search(window, "view_layer",scene, "view_layers",
                            new="scene.view_layer_add",
                            unlink="scene.view_layer_remove")


class VIEW3D_PT_view3d_properties(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "View"
    bl_label = "View Layer Info"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='',icon='INFO')

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rd = scene.render
        view_layer = context.view_layer

        col = layout.column(align=True)
        col.label(text="View Layer Properties:")
        col.prop(view_layer, "use", text="Use for Rendering")
        col.prop(rd, "use_single_layer", text="Render Single Layer")        

        col = layout.column(align=True)
        col.label(text="View Layer Passes:")
        col.prop(view_layer, "use_pass_combined")
        col.prop(view_layer, "use_pass_z")
        col.prop(view_layer, "use_pass_mist")
        col.prop(view_layer, "use_pass_normal")
        col.prop(view_layer, "use_pass_ambient_occlusion")
        col.prop(view_layer, "use_pass_subsurface_direct", text="Subsurface Direct")
        col.prop(view_layer, "use_pass_subsurface_color", text="Subsurface Color")


class VIEW3D_PT_view3d_camera_lock(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "View"
    bl_label = "View Camera Options"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='',icon='RESTRICT_RENDER_OFF')

    def draw(self, context):
        layout = self.layout
        # box = layout.box()
        # box.label(text="View Camera Options:")
        
        view = context.space_data

        layout.prop(view, "lens", text="Focal Length")

        subcol = layout.column(align=True)
        subcol.prop(view, "clip_start", text="Clip Start")
        subcol.prop(view, "clip_end", text="Clip End")

        row = layout.row()
        row.prop(view, "lock_camera")
        row.prop(view, "use_render_border")

        # subcol.separator()

        # subcol = layout.column()
        # subcol.enabled = not view.lock_camera_and_layers
        # row = subcol.row()
        # row.label(text="Local Camera:")
        # row.prop(view, "camera", text="")
        # # subcol.prop(view, "camera", text="Local Camera")

        # subcol = box.column(align=True)
        # subcol.prop(view, "use_render_border")
        # subcol.active = view.region_3d.view_perspective != 'CAMERA'

        # box = layout.box()
        # box.label(text="Active Camera Options:")
        # layout.use_property_split = True
        # layout.use_property_decorate = False  # No animation.

        # view = context.space_data

        # col = box.column(align=True)
        # subcol = col.column()
        # subcol.active = bool(view.region_3d.view_perspective != 'CAMERA' or view.region_quadviews)
        # row = subcol.row()
        # row.label(text="Lock to Object:")
        # row.prop(view, "lock_object",text="")
        # lock_object = view.lock_object
        # if lock_object:
        #     if lock_object.type == 'ARMATURE':
        #         subcol.prop_search(
        #             view, "lock_bone", lock_object.data,
        #             "edit_bones" if lock_object.mode == 'EDIT'
        #             else "bones",
        #             text=""
        #         )
        # else:
        #     subcol.prop(view, "lock_cursor", text="Lock to 3D Cursor")

        # col.prop(view, "lock_camera")


class VIEW3D_PT_view3d_cursor(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "View"
    bl_label = "3D Cursor"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='',icon='PIVOT_CURSOR')

    def draw(self, context):
        layout = self.layout

        cursor = context.scene.cursor

        layout.column().prop(cursor, "location", text="Location")
        rotation_mode = cursor.rotation_mode
        if rotation_mode == 'QUATERNION':
            layout.column().prop(cursor, "rotation_quaternion", text="Rotation")
        elif rotation_mode == 'AXIS_ANGLE':
            layout.column().prop(cursor, "rotation_axis_angle", text="Rotation")
        else:
            layout.column().prop(cursor, "rotation_euler", text="Rotation")
        layout.prop(cursor, "rotation_mode", text="")

class VIEW3D_PT_interface(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "View"
    bl_label = "Interface"

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="",icon='COLOR')

    def draw(self, context):
        layout = self.layout
        props = layout.operator("bp_general.split_region",text="Show Timeline",icon='TIME')
        props.space_type = 'DOPESHEET_EDITOR'
        props.space_sub_type = 'GPENCIL'
        props.split_direction = 'HORIZONTAL'
        props.split_factor = .2

        props = layout.operator("bp_general.split_region",text="Show Node Editor",icon='NODETREE')
        props.space_type = 'NODE_EDITOR'
        props.split_direction = 'VERTICAL'
        props.split_factor = .5

        props = layout.operator("bp_general.split_region",text="Show UV Editor",icon='UV')
        props.space_type = 'IMAGE_EDITOR'
        props.space_sub_type = 'UV'
        props.split_direction = 'VERTICAL'
        props.split_factor = .5

        props = layout.operator("bp_general.split_region",text="Show Text Editor",icon='TEXT')
        props.space_type = 'TEXT_EDITOR'
        props.split_direction = 'VERTICAL'
        props.split_factor = .5

        props = layout.operator("bp_general.split_region",text="Show Outliner",icon='OUTLINER')
        props.space_type = 'OUTLINER'
        props.split_direction = 'VERTICAL'
        props.split_factor = .2

        props = layout.operator("bp_general.split_region",text="Show Properties",icon='PROPERTIES')
        props.space_type = 'PROPERTIES'
        props.split_direction = 'VERTICAL'
        props.split_factor = .2



classes = (
    VIEW3D_PT_view_info,
    VIEW3D_PT_view3d_properties,
    VIEW3D_PT_view3d_camera_lock,
    VIEW3D_PT_view3d_cursor,
    VIEW3D_PT_interface,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()        