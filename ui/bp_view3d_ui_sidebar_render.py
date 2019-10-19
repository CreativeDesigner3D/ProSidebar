import bpy
from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        UIList,
        )

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
        props = scene.eevee

        box = layout.box()
        box.label(text="General",icon='PREFERENCES')

        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="Resolution:")
        row.prop(rd, "resolution_x", text="X")
        row.prop(rd, "resolution_y", text="Y")

        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="Frames:")        
        row.prop(scene, "frame_start", text="Start")
        row.prop(scene, "frame_end", text="End")

        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="Samples:")        
        row.prop(props, "taa_render_samples", text="Render")
        row.prop(props, "taa_samples", text="Viewport")

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


class BPRenderButtonsPanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Render"
    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        return (context.engine in cls.COMPAT_ENGINES)


class BPRENDER_PT_color_management(BPRenderButtonsPanel, Panel):
    bl_label = "Color Management"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 100
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene
        view = scene.view_settings

        flow = layout.grid_flow(row_major=True, columns=0, even_columns=False, even_rows=False, align=True)

        col = flow.column()
        col.prop(scene.display_settings, "display_device")

        col.separator()

        col.prop(view, "view_transform")
        col.prop(view, "look")

        col = flow.column()
        col.prop(view, "exposure")
        col.prop(view, "gamma")

        col.separator()

        col.prop(scene.sequencer_colorspace_settings, "name", text="Sequencer")


class BPRENDER_PT_color_management_curves(BPRenderButtonsPanel, Panel):
    bl_label = "Use Curves"
    bl_parent_id = "BPRENDER_PT_color_management"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}

    def draw_header(self, context):

        scene = context.scene
        view = scene.view_settings

        self.layout.prop(view, "use_curve_mapping", text="")

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        view = scene.view_settings

        layout.use_property_split = False
        layout.use_property_decorate = False  # No animation.

        layout.enabled = view.use_curve_mapping

        layout.template_curve_mapping(view, "curve_mapping", type='COLOR', levels=True)


class BPRENDER_PT_eevee_ambient_occlusion(BPRenderButtonsPanel, Panel):
    bl_label = "Ambient Occlusion"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_EEVEE'}

    @classmethod
    def poll(cls, context):
        return (context.engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
        scene = context.scene
        props = scene.eevee
        self.layout.prop(props, "use_gtao", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene
        props = scene.eevee

        layout.active = props.use_gtao
        col = layout.column()
        col.prop(props, "gtao_distance")
        col.prop(props, "gtao_factor")
        col.prop(props, "gtao_quality")
        col.prop(props, "use_gtao_bent_normals")
        col.prop(props, "use_gtao_bounce")


class BPRENDER_PT_eevee_motion_blur(BPRenderButtonsPanel, Panel):
    bl_label = "Motion Blur"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_EEVEE'}

    @classmethod
    def poll(cls, context):
        return (context.engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
        scene = context.scene
        props = scene.eevee
        self.layout.prop(props, "use_motion_blur", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene
        props = scene.eevee

        layout.active = props.use_motion_blur
        col = layout.column()
        col.prop(props, "motion_blur_samples")
        col.prop(props, "motion_blur_shutter")


class BPRENDER_PT_eevee_depth_of_field(BPRenderButtonsPanel, Panel):
    bl_label = "Depth of Field"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_EEVEE'}

    @classmethod
    def poll(cls, context):
        return (context.engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene
        props = scene.eevee

        col = layout.column()
        col.prop(props, "bokeh_max_size")
        # Not supported yet
        # col.prop(props, "bokeh_threshold")


class BPRENDER_PT_eevee_bloom(BPRenderButtonsPanel, Panel):
    bl_label = "Bloom"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_EEVEE'}

    @classmethod
    def poll(cls, context):
        return (context.engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
        scene = context.scene
        props = scene.eevee
        self.layout.prop(props, "use_bloom", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.eevee

        layout.active = props.use_bloom
        col = layout.column()
        col.prop(props, "bloom_threshold")
        col.prop(props, "bloom_knee")
        col.prop(props, "bloom_radius")
        col.prop(props, "bloom_color")
        col.prop(props, "bloom_intensity")
        col.prop(props, "bloom_clamp")


class BPRENDER_PT_eevee_volumetric(BPRenderButtonsPanel, Panel):
    bl_label = "Volumetric"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_EEVEE'}

    @classmethod
    def poll(cls, context):
        return (context.engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.eevee

        col = layout.column(align=True)
        col.prop(props, "volumetric_start")
        col.prop(props, "volumetric_end")

        col = layout.column()
        col.prop(props, "volumetric_tile_size")
        col.prop(props, "volumetric_samples")
        col.prop(props, "volumetric_sample_distribution", text="Distribution")


class BPRENDER_PT_eevee_volumetric_lighting(BPRenderButtonsPanel, Panel):
    bl_label = "Volumetric Lighting"
    bl_parent_id = "BPRENDER_PT_eevee_volumetric"
    COMPAT_ENGINES = {'BLENDER_EEVEE'}

    def draw_header(self, context):
        scene = context.scene
        props = scene.eevee
        self.layout.prop(props, "use_volumetric_lights", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.eevee

        layout.active = props.use_volumetric_lights
        layout.prop(props, "volumetric_light_clamp", text="Light Clamping")


class BPRENDER_PT_eevee_volumetric_shadows(BPRenderButtonsPanel, Panel):
    bl_label = "Volumetric Shadows"
    bl_parent_id = "BPRENDER_PT_eevee_volumetric"
    COMPAT_ENGINES = {'BLENDER_EEVEE'}

    def draw_header(self, context):
        scene = context.scene
        props = scene.eevee
        self.layout.prop(props, "use_volumetric_shadows", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.eevee

        layout.active = props.use_volumetric_shadows
        layout.prop(props, "volumetric_shadow_samples", text="Shadow Samples")


class BPRENDER_PT_eevee_subsurface_scattering(BPRenderButtonsPanel, Panel):
    bl_label = "Subsurface Scattering"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_EEVEE'}

    @classmethod
    def poll(cls, context):
        return (context.engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.eevee

        col = layout.column()
        col.prop(props, "sss_samples")
        col.prop(props, "sss_jitter_threshold")
        col.prop(props, "use_sss_separate_albedo")


class BPRENDER_PT_eevee_screen_space_reflections(BPRenderButtonsPanel, Panel):
    bl_label = "Screen Space Reflections"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_EEVEE'}

    @classmethod
    def poll(cls, context):
        return (context.engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
        scene = context.scene
        props = scene.eevee
        self.layout.prop(props, "use_ssr", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.eevee

        col = layout.column()
        col.active = props.use_ssr
        col.prop(props, "use_ssr_refraction", text="Refraction")
        col.prop(props, "use_ssr_halfres")
        col.prop(props, "ssr_quality")
        col.prop(props, "ssr_max_roughness")
        col.prop(props, "ssr_thickness")
        col.prop(props, "ssr_border_fade")
        col.prop(props, "ssr_firefly_fac")


class BPRENDER_PT_eevee_shadows(BPRenderButtonsPanel, Panel):
    bl_label = "Shadows"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_EEVEE'}

    @classmethod
    def poll(cls, context):
        return (context.engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.eevee

        col = layout.column()
        col.prop(props, "shadow_method")
        col.prop(props, "shadow_cube_size", text="Cube Size")
        col.prop(props, "shadow_cascade_size", text="Cascade Size")
        col.prop(props, "use_shadow_high_bitdepth")
        col.prop(props, "use_soft_shadows")
        col.prop(props, "light_threshold")


class BPRENDER_PT_eevee_sampling(BPRenderButtonsPanel, Panel):
    bl_label = "Sampling"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_EEVEE'}

    @classmethod
    def poll(cls, context):
        return (context.engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene
        props = scene.eevee

        col = layout.column(align=True)
        col.prop(props, "taa_render_samples", text="Render")
        col.prop(props, "taa_samples", text="Viewport")

        col = layout.column()
        col.prop(props, "use_taa_reprojection")


class BPRENDER_PT_eevee_indirect_lighting(BPRenderButtonsPanel, Panel):
    bl_label = "Indirect Lighting"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_EEVEE'}

    @classmethod
    def poll(cls, context):
        return (context.engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene
        props = scene.eevee

        col = layout.column()
        col.operator("scene.light_cache_bake", text="Bake Indirect Lighting", icon='RENDER_STILL')
        col.operator("scene.light_cache_bake", text="Bake Cubemap Only", icon='LIGHTPROBE_CUBEMAP').subset = 'CUBEMAPS'
        col.operator("scene.light_cache_free", text="Delete Lighting Cache")

        cache_info = scene.eevee.gi_cache_info
        if cache_info:
            col.label(text=cache_info)

        col.prop(props, "gi_auto_bake")

        col.prop(props, "gi_diffuse_bounces")
        col.prop(props, "gi_cubemap_resolution")
        col.prop(props, "gi_visibility_resolution", text="Diffuse Occlusion")
        col.prop(props, "gi_irradiance_smoothing")
        col.prop(props, "gi_glossy_clamp")
        col.prop(props, "gi_filter_quality")


class BPRENDER_PT_eevee_indirect_lighting_display(BPRenderButtonsPanel, Panel):
    bl_label = "Display"
    bl_parent_id = "BPRENDER_PT_eevee_indirect_lighting"
    COMPAT_ENGINES = {'BLENDER_EEVEE'}

    @classmethod
    def poll(cls, context):
        return (context.engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene
        props = scene.eevee

        row = layout.row(align=True)
        row.prop(props, "gi_cubemap_display_size", text="Cubemap Size")
        row.prop(props, "gi_show_cubemaps", text="", toggle=True)

        row = layout.row(align=True)
        row.prop(props, "gi_irradiance_display_size", text="Irradiance Size")
        row.prop(props, "gi_show_irradiance", text="", toggle=True)


class BPRENDER_PT_eevee_film(BPRenderButtonsPanel, Panel):
    bl_label = "Film"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_EEVEE'}

    @classmethod
    def poll(cls, context):
        return (context.engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        rd = scene.render

        col = layout.column()
        col.prop(rd, "filter_size")
        col.prop(rd, "film_transparent", text="Transparent")


class BPRENDER_PT_eevee_film_overscan(BPRenderButtonsPanel, Panel):
    bl_label = "Overscan"
    bl_parent_id = "BPRENDER_PT_eevee_film"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_EEVEE'}

    def draw_header(self, context):

        scene = context.scene
        props = scene.eevee

        self.layout.prop(props, "use_overscan", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene
        props = scene.eevee

        layout.active = props.use_overscan
        layout.prop(props, "overscan_size", text="Size")


class BPRENDER_PT_eevee_hair(BPRenderButtonsPanel, Panel):
    bl_label = "Hair"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_EEVEE'}

    @classmethod
    def poll(cls, context):
        return (context.engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rd = scene.render

        layout.use_property_split = True

        layout.prop(rd, "hair_type", expand=True)
        layout.prop(rd, "hair_subdiv")


class BPRENDER_PT_opengl_sampling(BPRenderButtonsPanel, Panel):
    bl_label = "Sampling"
    COMPAT_ENGINES = {'BLENDER_WORKBENCH'}

    @classmethod
    def poll(cls, context):
        return (context.engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene
        props = scene.display

        col = layout.column()
        col.prop(props, "render_aa", text="Render")
        col.prop(props, "viewport_aa", text="Viewport Render")


class BPRENDER_PT_opengl_film(BPRenderButtonsPanel, Panel):
    bl_label = "Film"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_WORKBENCH'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        rd = context.scene.render
        layout.prop(rd, "film_transparent", text="Transparent")


# class BPRENDER_PT_opengl_lighting(BPRenderButtonsPanel, Panel):
#     bl_label = "Lighting"
#     COMPAT_ENGINES = {'BLENDER_WORKBENCH'}

#     @classmethod
#     def poll(cls, context):
#         return (context.engine in cls.COMPAT_ENGINES)

#     def draw(self, context):
#         VIEW3D_PT_shading_lighting.draw(self, context)


# class BPRENDER_PT_opengl_color(BPRenderButtonsPanel, Panel):
#     bl_label = "Color"
#     COMPAT_ENGINES = {'BLENDER_WORKBENCH'}

#     @classmethod
#     def poll(cls, context):
#         return (context.engine in cls.COMPAT_ENGINES)

#     def draw(self, context):
#         VIEW3D_PT_shading_color._draw_color_type(self, context)


# class BPRENDER_PT_opengl_options(BPRenderButtonsPanel, Panel):
#     bl_label = "Options"
#     COMPAT_ENGINES = {'BLENDER_WORKBENCH'}

#     @classmethod
#     def poll(cls, context):
#         return (context.engine in cls.COMPAT_ENGINES)

#     def draw(self, context):
#         VIEW3D_PT_shading_options.draw(self, context)


class BPRENDER_PT_simplify(BPRenderButtonsPanel, Panel):
    bl_label = "Simplify"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}

    def draw_header(self, context):
        rd = context.scene.render
        self.layout.prop(rd, "use_simplify", text="")

    def draw(self, context):
        pass


class BPRENDER_PT_simplify_viewport(BPRenderButtonsPanel, Panel):
    bl_label = "Viewport"
    bl_parent_id = "BPRENDER_PT_simplify"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        rd = context.scene.render

        layout.active = rd.use_simplify

        flow = layout.grid_flow(row_major=True, columns=0, even_columns=False, even_rows=False, align=True)

        col = flow.column()
        col.prop(rd, "simplify_subdivision", text="Max Subdivision")

        col = flow.column()
        col.prop(rd, "simplify_child_particles", text="Max Child Particles")

        col = flow.column()
        col.prop(rd, "use_simplify_smoke_highres", text="High-resolution Smoke")


class BPRENDER_PT_simplify_render(BPRenderButtonsPanel, Panel):
    bl_label = "Render"
    bl_parent_id = "BPRENDER_PT_simplify"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        rd = context.scene.render

        layout.active = rd.use_simplify

        flow = layout.grid_flow(row_major=True, columns=0, even_columns=False, even_rows=False, align=True)

        col = flow.column()
        col.prop(rd, "simplify_subdivision_render", text="Max Subdivision")

        col = flow.column()
        col.prop(rd, "simplify_child_particles_render", text="Max Child Particles")


class BPRENDER_PT_simplify_greasepencil(BPRenderButtonsPanel, Panel):
    bl_label = "Grease Pencil"
    bl_parent_id = "BPRENDER_PT_simplify"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME', 'BLENDER_CLAY', 'BLENDER_EEVEE'}
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        rd = context.scene.render
        self.layout.prop(rd, "simplify_gpencil", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        rd = context.scene.render

        layout.active = rd.simplify_gpencil

        col = layout.column()
        col.prop(rd, "simplify_gpencil_onplay", text="Playback Only")
        col.prop(rd, "simplify_gpencil_view_modifier", text="Modifiers")
        col.prop(rd, "simplify_gpencil_shader_fx", text="ShaderFX")
        col.prop(rd, "simplify_gpencil_blend", text="Layers Blending")

        col.prop(rd, "simplify_gpencil_view_fill")
        sub = col.column()
        sub.active = rd.simplify_gpencil_view_fill
        sub.prop(rd, "simplify_gpencil_remove_lines", text="Lines")

class BPRenderFreestyleButtonsPanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Render"
    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        scene = context.scene
        with_freestyle = bpy.app.build_options.freestyle
        return scene and with_freestyle and(context.engine in cls.COMPAT_ENGINES)


class BPRENDER_PT_freestyle(BPRenderFreestyleButtonsPanel, Panel):
    bl_label = "Freestyle"
    bl_options = {'DEFAULT_CLOSED'}
    # bl_order = 10
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE'}

    def draw_header(self, context):
        rd = context.scene.render
        self.layout.prop(rd, "use_freestyle", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        rd = context.scene.render

        layout.active = rd.use_freestyle

        layout.prop(rd, "line_thickness_mode", expand=True)

        if (rd.line_thickness_mode == 'ABSOLUTE'):
            layout.prop(rd, "line_thickness")


classes = (
    VIEW3D_PT_render,
    VIEW3D_PT_output_settings,
    BPRENDER_PT_eevee_ambient_occlusion,
    BPRENDER_PT_eevee_screen_space_reflections,
    BPRENDER_PT_eevee_bloom,
    BPRENDER_PT_freestyle,
    BPRENDER_PT_eevee_sampling,
    BPRENDER_PT_color_management,
    BPRENDER_PT_color_management_curves,
    BPRENDER_PT_eevee_motion_blur,
    BPRENDER_PT_eevee_depth_of_field,
    BPRENDER_PT_eevee_volumetric,
    BPRENDER_PT_eevee_volumetric_lighting,
    BPRENDER_PT_eevee_volumetric_shadows,
    BPRENDER_PT_eevee_subsurface_scattering,
    BPRENDER_PT_eevee_shadows,
    BPRENDER_PT_eevee_indirect_lighting,
    BPRENDER_PT_eevee_indirect_lighting_display,
    BPRENDER_PT_eevee_film,
    BPRENDER_PT_eevee_film_overscan,
    BPRENDER_PT_eevee_hair,
    BPRENDER_PT_opengl_sampling,
    BPRENDER_PT_opengl_film,
    BPRENDER_PT_simplify,
    BPRENDER_PT_simplify_viewport,
    BPRENDER_PT_simplify_render,
    BPRENDER_PT_simplify_greasepencil
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                