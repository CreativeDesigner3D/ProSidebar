import bpy
from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        UIList,
        )

#TODO: ADD EEVEE RENDERING SETTINGS
#TODO: ADD CYCLES RENDERING SETTINGS
#TODO: ADD WORKBENCH RENDERING SETTINGS

class RenderPanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Render"
    bl_category = "Render"
    # bl_options = {'HIDE_HEADER'}
    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    # @classmethod
    # def poll(cls, context):
    #     return (context.engine in cls.COMPAT_ENGINES)

class VIEW3D_PT_render(Panel, RenderPanel):
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rd = scene.render

        if rd.has_multiple_engines:
            row = layout.row()
            row.scale_y = 1.3
            # row.label(text="Render Engine")
            row.prop(rd, "engine", text="Render Engine",expand=True)

        row = layout.row()
        row.scale_y = 1.3            
        row.operator('render.render',icon='RESTRICT_RENDER_OFF',text="Render Image").use_viewport=True
        props = row.operator('render.render',text='Render Animation',icon='RENDER_ANIMATION')
        props.animation=True
        props.use_viewport=True


class VIEW3D_PT_output_settings(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Output Settings"
    bl_category = "Render"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text='',icon='OUTPUT')

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rd = scene.render

        col = layout.column(align=True)
        row = col.row(align=True)
        row.label(text="Resolution:")
        row.prop(rd, "resolution_x", text="X")
        row.prop(rd, "resolution_y", text="Y")
        # row = col.row(align=True)
        # row.label(text=" ")
        # row.prop(rd, "resolution_percentage", text="%")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.label(text="Frames:")        
        row.prop(scene, "frame_start", text="Start")
        row.prop(scene, "frame_end", text="End")
        # col.prop(scene, "frame_step", text="Step")

        image_settings = rd.image_settings
        ffmpeg = rd.ffmpeg

        box = layout.box()
        box.label(text="Output File Type",icon='FILEBROWSER')
        box.prop(rd, "filepath", text="Path")        
        box.template_image_settings(image_settings, color_management=False)

        if image_settings.file_format in {'FFMPEG', 'XVID', 'H264', 'THEORA'}:
            box.prop(ffmpeg, "format")
        
        #NEEDS CODEC
        if ffmpeg.format in {'AVI', 'QUICKTIME', 'MKV', 'OGG', 'MPEG4'}:
            box.prop(ffmpeg, "codec")

        box = layout.box()
        box.label(text="Audio Settings:",icon='FILE_SOUND')

        if ffmpeg.format != 'MP3':
            row = box.row()
            row.label(text="Audio Codec:")
            row.prop(ffmpeg, "audio_codec", text="")

        if ffmpeg.audio_codec != 'NONE':
            box.prop(ffmpeg, "audio_bitrate")
            box.prop(ffmpeg, "audio_volume", slider=True)


class VIEW3D_PT_eevee_render_settings(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Eevee Render Settings"
    bl_category = "Render"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text='',icon='SETTINGS')

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.eevee

        col = layout.column(align=True)
        col.label(text="Sampling")
        row = col.row()
        row.prop(props, "taa_samples", text="Viewport")
        row.prop(props, "taa_render_samples", text="Render")

        # col.prop(props, "use_taa_reprojection")

        layout.prop(props, "use_gtao")
        if props.use_gtao:
            col = layout.column()
            col.prop(props, "gtao_distance")
            col.prop(props, "gtao_factor")
            col.prop(props, "gtao_quality")
            col.prop(props, "use_gtao_bent_normals")
            col.prop(props, "use_gtao_bounce")

        layout.prop(props, "use_motion_blur")
        if props.use_motion_blur:
            col = layout.column()
            col.prop(props, "motion_blur_samples")
            col.prop(props, "motion_blur_shutter")

        layout.prop(props,"use_dof")
        if props.use_dof:
            col = layout.column()
            col.prop(props, "bokeh_max_size")

        layout.prop(props, "use_bloom")
        if props.use_bloom:
            col = layout.column()
            col.prop(props, "bloom_threshold")
            col.prop(props, "bloom_knee")
            col.prop(props, "bloom_radius")
            col.prop(props, "bloom_color")
            col.prop(props, "bloom_intensity")
            col.prop(props, "bloom_clamp")        

classes = (
    VIEW3D_PT_render,
    VIEW3D_PT_output_settings,
    VIEW3D_PT_eevee_render_settings,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                