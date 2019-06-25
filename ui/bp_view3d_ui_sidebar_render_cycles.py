import bpy
from bpy_extras.node_utils import find_node_input
from bl_ui.utils import PresetPanel

from bpy.types import Panel

class BPCYCLES_PT_sampling_presets(PresetPanel, Panel):
    bl_label = "Sampling Presets"
    preset_subdir = "cycles/sampling"
    preset_operator = "script.execute_preset"
    preset_add_operator = "render.cycles_sampling_preset_add"
    COMPAT_ENGINES = {'CYCLES'}


class BPCYCLES_PT_integrator_presets(PresetPanel, Panel):
    bl_label = "Integrator Presets"
    preset_subdir = "cycles/integrator"
    preset_operator = "script.execute_preset"
    preset_add_operator = "render.cycles_integrator_preset_add"
    COMPAT_ENGINES = {'CYCLES'}

class BPCyclesButtonsPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    # bl_label = "Render"
    bl_category = "Render"
    COMPAT_ENGINES = {'CYCLES'}

    @classmethod
    def poll(cls, context):
        return context.engine in cls.COMPAT_ENGINES


def get_device_type(context):
    return context.preferences.addons["cycles"].preferences.compute_device_type


def use_cpu(context):
    cscene = context.scene.cycles

    return (get_device_type(context) == 'NONE' or cscene.device == 'CPU')


def use_opencl(context):
    cscene = context.scene.cycles

    return (get_device_type(context) == 'OPENCL' and cscene.device == 'GPU')


def use_cuda(context):
    cscene = context.scene.cycles

    return (get_device_type(context) == 'CUDA' and cscene.device == 'GPU')


def use_branched_path(context):
    cscene = context.scene.cycles

    return (cscene.progressive == 'BRANCHED_PATH')


def use_sample_all_lights(context):
    cscene = context.scene.cycles

    return cscene.sample_all_lights_direct or cscene.sample_all_lights_indirect


def show_device_active(context):
    cscene = context.scene.cycles
    if cscene.device != 'GPU':
        return True
    return context.preferences.addons[__package__].preferences.has_active_device()


def draw_samples_info(layout, context):
    cscene = context.scene.cycles
    integrator = cscene.progressive

    # Calculate sample values
    if integrator == 'PATH':
        aa = cscene.samples
        if cscene.use_square_samples:
            aa = aa * aa
    else:
        aa = cscene.aa_samples
        d = cscene.diffuse_samples
        g = cscene.glossy_samples
        t = cscene.transmission_samples
        ao = cscene.ao_samples
        ml = cscene.mesh_light_samples
        sss = cscene.subsurface_samples
        vol = cscene.volume_samples

        if cscene.use_square_samples:
            aa = aa * aa
            d = d * d
            g = g * g
            t = t * t
            ao = ao * ao
            ml = ml * ml
            sss = sss * sss
            vol = vol * vol

    # Draw interface
    # Do not draw for progressive, when Square Samples are disabled
    if use_branched_path(context) or (cscene.use_square_samples and integrator == 'PATH'):
        col = layout.column(align=True)
        col.scale_y = 0.6
        col.label(text="Total Samples:")
        col.separator()
        if integrator == 'PATH':
            col.label(text="%s AA" % aa)
        else:
            col.label(text="%s AA, %s Diffuse, %s Glossy, %s Transmission" %
                      (aa, d * aa, g * aa, t * aa))
            col.separator()
            col.label(text="%s AO, %s Mesh Light, %s Subsurface, %s Volume" %
                      (ao * aa, ml * aa, sss * aa, vol * aa))


class BPCYCLES_RENDER_PT_sampling(BPCyclesButtonsPanel, Panel):
    bl_label = "Sampling"

    def draw_header_preset(self, context):
        BPCYCLES_PT_sampling_presets.draw_panel_header(self.layout)

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        cscene = scene.cycles

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(cscene, "progressive")

        if cscene.progressive == 'PATH' or use_branched_path(context) is False:
            col = layout.column(align=True)
            col.prop(cscene, "samples", text="Render")
            col.prop(cscene, "preview_samples", text="Viewport")

            draw_samples_info(layout, context)
        else:
            col = layout.column(align=True)
            col.prop(cscene, "aa_samples", text="Render")
            col.prop(cscene, "preview_aa_samples", text="Viewport")


class BPCYCLES_RENDER_PT_sampling_sub_samples(BPCyclesButtonsPanel, Panel):
    bl_label = "Sub Samples"
    bl_parent_id = "BPCYCLES_RENDER_PT_sampling"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        cscene = scene.cycles
        return cscene.progressive != 'PATH' and use_branched_path(context)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        cscene = scene.cycles

        col = layout.column(align=True)
        col.prop(cscene, "diffuse_samples", text="Diffuse")
        col.prop(cscene, "glossy_samples", text="Glossy")
        col.prop(cscene, "transmission_samples", text="Transmission")
        col.prop(cscene, "ao_samples", text="AO")

        sub = col.row(align=True)
        sub.active = use_sample_all_lights(context)
        sub.prop(cscene, "mesh_light_samples", text="Mesh Light")
        col.prop(cscene, "subsurface_samples", text="Subsurface")
        col.prop(cscene, "volume_samples", text="Volume")

        draw_samples_info(layout, context)


class BPCYCLES_RENDER_PT_sampling_advanced(BPCyclesButtonsPanel, Panel):
    bl_label = "Advanced"
    bl_parent_id = "BPCYCLES_RENDER_PT_sampling"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        cscene = scene.cycles

        row = layout.row(align=True)
        row.prop(cscene, "seed")
        row.prop(cscene, "use_animated_seed", text="", icon='TIME')

        layout.prop(cscene, "sampling_pattern", text="Pattern")

        layout.prop(cscene, "use_square_samples")

        layout.separator()

        col = layout.column(align=True)
        col.prop(cscene, "light_sampling_threshold", text="Light Threshold")

        if cscene.progressive != 'PATH' and use_branched_path(context):
            col = layout.column(align=True)
            col.prop(cscene, "sample_all_lights_direct")
            col.prop(cscene, "sample_all_lights_indirect")

        for view_layer in scene.view_layers:
            if view_layer.samples > 0:
                layout.separator()
                layout.row().prop(cscene, "use_layer_samples")
                break


class BPCYCLES_RENDER_PT_sampling_total(BPCyclesButtonsPanel, Panel):
    bl_label = "Total Samples"
    bl_parent_id = "BPCYCLES_RENDER_PT_sampling"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        cscene = scene.cycles

        if cscene.use_square_samples:
            return True

        return cscene.progressive != 'PATH' and use_branched_path(context)

    def draw(self, context):
        layout = self.layout
        cscene = context.scene.cycles
        integrator = cscene.progressive

        # Calculate sample values
        if integrator == 'PATH':
            aa = cscene.samples
            if cscene.use_square_samples:
                aa = aa * aa
        else:
            aa = cscene.aa_samples
            d = cscene.diffuse_samples
            g = cscene.glossy_samples
            t = cscene.transmission_samples
            ao = cscene.ao_samples
            ml = cscene.mesh_light_samples
            sss = cscene.subsurface_samples
            vol = cscene.volume_samples

            if cscene.use_square_samples:
                aa = aa * aa
                d = d * d
                g = g * g
                t = t * t
                ao = ao * ao
                ml = ml * ml
                sss = sss * sss
                vol = vol * vol

        col = layout.column(align=True)
        col.scale_y = 0.6
        if integrator == 'PATH':
            col.label(text="%s AA" % aa)
        else:
            col.label(text="%s AA, %s Diffuse, %s Glossy, %s Transmission" %
                      (aa, d * aa, g * aa, t * aa))
            col.separator()
            col.label(text="%s AO, %s Mesh Light, %s Subsurface, %s Volume" %
                      (ao * aa, ml * aa, sss * aa, vol * aa))


class BPCYCLES_RENDER_PT_subdivision(BPCyclesButtonsPanel, Panel):
    bl_label = "Subdivision"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.scene.render.engine == 'CYCLES') and (context.scene.cycles.feature_set == 'EXPERIMENTAL')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        cscene = scene.cycles

        col = layout.column()
        sub = col.column(align=True)
        sub.prop(cscene, "dicing_rate", text="Dicing Rate Render")
        sub.prop(cscene, "preview_dicing_rate", text="Preview")

        col.separator()

        col.prop(cscene, "offscreen_dicing_scale", text="Offscreen Scale")
        col.prop(cscene, "max_subdivisions")

        col.prop(cscene, "dicing_camera")


class BPCYCLES_RENDER_PT_hair(BPCyclesButtonsPanel, Panel):
    bl_label = "Hair"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        scene = context.scene
        ccscene = scene.cycles_curves

        layout.prop(ccscene, "use_curves", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        ccscene = scene.cycles_curves

        layout.active = ccscene.use_curves

        col = layout.column()
        col.prop(ccscene, "shape", text="Shape")
        if not (ccscene.primitive in {'CURVE_SEGMENTS', 'LINE_SEGMENTS'} and ccscene.shape == 'RIBBONS'):
            col.prop(ccscene, "cull_backfacing", text="Cull back-faces")
        col.prop(ccscene, "primitive", text="Primitive")

        if ccscene.primitive == 'TRIANGLES' and ccscene.shape == 'THICK':
            col.prop(ccscene, "resolution", text="Resolution")
        elif ccscene.primitive == 'CURVE_SEGMENTS':
            col.prop(ccscene, "subdivisions", text="Curve subdivisions")


class BPCYCLES_RENDER_PT_volumes(BPCyclesButtonsPanel, Panel):
    bl_label = "Volumes"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        cscene = scene.cycles

        col = layout.column()
        col.prop(cscene, "volume_step_size", text="Step Size")
        col.prop(cscene, "volume_max_steps", text="Max Steps")


class BPCYCLES_RENDER_PT_light_paths(BPCyclesButtonsPanel, Panel):
    bl_label = "Light Paths"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header_preset(self, context):
        BPCYCLES_PT_integrator_presets.draw_panel_header(self.layout)

    def draw(self, context):
        pass


class BPCYCLES_RENDER_PT_light_paths_max_bounces(BPCyclesButtonsPanel, Panel):
    bl_label = "Max Bounces"
    bl_parent_id = "BPCYCLES_RENDER_PT_light_paths"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        cscene = scene.cycles

        col = layout.column(align=True)
        col.prop(cscene, "max_bounces", text="Total")

        col = layout.column(align=True)
        col.prop(cscene, "diffuse_bounces", text="Diffuse")
        col.prop(cscene, "glossy_bounces", text="Glossy")
        col.prop(cscene, "transparent_max_bounces", text="Transparency")
        col.prop(cscene, "transmission_bounces", text="Transmission")
        col.prop(cscene, "volume_bounces", text="Volume")


class BPCYCLES_RENDER_PT_light_paths_clamping(BPCyclesButtonsPanel, Panel):
    bl_label = "Clamping"
    bl_parent_id = "BPCYCLES_RENDER_PT_light_paths"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        cscene = scene.cycles

        col = layout.column(align=True)
        col.prop(cscene, "sample_clamp_direct", text="Direct Light")
        col.prop(cscene, "sample_clamp_indirect", text="Indirect Light")


class BPCYCLES_RENDER_PT_light_paths_caustics(BPCyclesButtonsPanel, Panel):
    bl_label = "Caustics"
    bl_parent_id = "BPCYCLES_RENDER_PT_light_paths"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        cscene = scene.cycles

        col = layout.column()
        col.prop(cscene, "blur_glossy")
        col.prop(cscene, "caustics_reflective")
        col.prop(cscene, "caustics_refractive")


class BPCYCLES_RENDER_PT_motion_blur(BPCyclesButtonsPanel, Panel):
    bl_label = "Motion Blur"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        rd = context.scene.render

        self.layout.prop(rd, "use_motion_blur", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        cscene = scene.cycles
        rd = scene.render
        layout.active = rd.use_motion_blur

        col = layout.column()
        col.prop(cscene, "motion_blur_position", text="Position")
        col.prop(rd, "motion_blur_shutter")
        col.separator()
        col.prop(cscene, "rolling_shutter_type", text="Rolling Shutter")
        sub = col.column()
        sub.active = cscene.rolling_shutter_type != 'NONE'
        sub.prop(cscene, "rolling_shutter_duration")


class BPCYCLES_RENDER_PT_motion_blur_curve(BPCyclesButtonsPanel, Panel):
    bl_label = "Shutter Curve"
    bl_parent_id = "BPCYCLES_RENDER_PT_motion_blur"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        rd = scene.render
        layout.active = rd.use_motion_blur

        col = layout.column()

        col.template_curve_mapping(rd, "motion_blur_shutter_curve")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("render.shutter_curve_preset", icon='SMOOTHCURVE', text="").shape = 'SMOOTH'
        row.operator("render.shutter_curve_preset", icon='SPHERECURVE', text="").shape = 'ROUND'
        row.operator("render.shutter_curve_preset", icon='ROOTCURVE', text="").shape = 'ROOT'
        row.operator("render.shutter_curve_preset", icon='SHARPCURVE', text="").shape = 'SHARP'
        row.operator("render.shutter_curve_preset", icon='LINCURVE', text="").shape = 'LINE'
        row.operator("render.shutter_curve_preset", icon='NOCURVE', text="").shape = 'MAX'


class BPCYCLES_RENDER_PT_film(BPCyclesButtonsPanel, Panel):
    bl_label = "Film"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        scene = context.scene
        cscene = scene.cycles

        col = layout.column()
        col.prop(cscene, "film_exposure")


class BPCYCLES_RENDER_PT_film_transparency(BPCyclesButtonsPanel, Panel):
    bl_label = "Transparent"
    bl_parent_id = "BPCYCLES_RENDER_PT_film"

    def draw_header(self, context):
        layout = self.layout

        scene = context.scene
        rd = scene.render

        layout.prop(rd, "film_transparent", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        scene = context.scene
        rd = scene.render
        cscene = scene.cycles

        layout.active = rd.film_transparent

        col = layout.column()
        col.prop(cscene, "film_transparent_glass", text="Transparent Glass")

        sub = col.column()
        sub.active = rd.film_transparent and cscene.film_transparent_glass
        sub.prop(cscene, "film_transparent_roughness", text="Roughness Threshold")


class BPCYCLES_RENDER_PT_film_pixel_filter(BPCyclesButtonsPanel, Panel):
    bl_label = "Pixel Filter"
    bl_parent_id = "BPCYCLES_RENDER_PT_film"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        scene = context.scene
        cscene = scene.cycles

        col = layout.column()
        col.prop(cscene, "pixel_filter_type", text="Type")
        if cscene.pixel_filter_type != 'BOX':
            col.prop(cscene, "filter_width", text="Width")


class BPCYCLES_RENDER_PT_performance(BPCyclesButtonsPanel, Panel):
    bl_label = "Performance"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        pass


class BPCYCLES_RENDER_PT_performance_threads(BPCyclesButtonsPanel, Panel):
    bl_label = "Threads"
    bl_parent_id = "BPCYCLES_RENDER_PT_performance"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        rd = scene.render

        col = layout.column()

        col.prop(rd, "threads_mode")
        sub = col.column(align=True)
        sub.enabled = rd.threads_mode == 'FIXED'
        sub.prop(rd, "threads")


class BPCYCLES_RENDER_PT_performance_tiles(BPCyclesButtonsPanel, Panel):
    bl_label = "Tiles"
    bl_parent_id = "BPCYCLES_RENDER_PT_performance"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        rd = scene.render
        cscene = scene.cycles

        col = layout.column()

        sub = col.column(align=True)
        sub.prop(rd, "tile_x", text="Tiles X")
        sub.prop(rd, "tile_y", text="Y")
        col.prop(cscene, "tile_order", text="Order")

        sub = col.column()
        sub.active = not rd.use_save_buffers
        for view_layer in scene.view_layers:
            if view_layer.cycles.use_denoising:
                sub.active = False
        sub.prop(cscene, "use_progressive_refine")


class BPCYCLES_RENDER_PT_performance_acceleration_structure(BPCyclesButtonsPanel, Panel):
    bl_label = "Acceleration Structure"
    bl_parent_id = "BPCYCLES_RENDER_PT_performance"

    def draw(self, context):
        import _cycles

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        cscene = scene.cycles

        col = layout.column()

        if _cycles.with_embree:
            row = col.row()
            row.active = use_cpu(context)
            row.prop(cscene, "use_bvh_embree")
        col.prop(cscene, "debug_use_spatial_splits")
        sub = col.column()
        sub.active = not cscene.use_bvh_embree or not _cycles.with_embree
        sub.prop(cscene, "debug_use_hair_bvh")
        sub = col.column()
        sub.active = not cscene.debug_use_spatial_splits and not cscene.use_bvh_embree
        sub.prop(cscene, "debug_bvh_time_steps")


class BPCYCLES_RENDER_PT_performance_final_render(BPCyclesButtonsPanel, Panel):
    bl_label = "Final Render"
    bl_parent_id = "BPCYCLES_RENDER_PT_performance"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        rd = scene.render

        col = layout.column()

        col.prop(rd, "use_save_buffers")
        col.prop(rd, "use_persistent_data", text="Persistent Images")


class BPCYCLES_RENDER_PT_performance_viewport(BPCyclesButtonsPanel, Panel):
    bl_label = "Viewport"
    bl_parent_id = "BPCYCLES_RENDER_PT_performance"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        rd = scene.render
        cscene = scene.cycles

        col = layout.column()
        col.prop(rd, "preview_pixel_size", text="Pixel Size")
        col.prop(cscene, "preview_start_resolution", text="Start Pixels")


class BPCYCLES_RENDER_PT_filter(BPCyclesButtonsPanel, Panel):
    bl_label = "Filter"
    bl_options = {'DEFAULT_CLOSED'}
    # bl_context = "view_layer"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        with_freestyle = bpy.app.build_options.freestyle

        scene = context.scene
        rd = scene.render
        view_layer = context.view_layer

        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)

        col = flow.column()
        col.prop(view_layer, "use_sky", text="Environment")
        col = flow.column()
        col.prop(view_layer, "use_ao", text="Ambient Occlusion")
        col = flow.column()
        col.prop(view_layer, "use_solid", text="Surfaces")
        col = flow.column()
        col.prop(view_layer, "use_strand", text="Hair")
        if with_freestyle:
            col = flow.column()
            col.prop(view_layer, "use_freestyle", text="Freestyle")
            col.active = rd.use_freestyle


class BPCYCLES_RENDER_PT_override(BPCyclesButtonsPanel, Panel):
    bl_label = "Override"
    bl_options = {'DEFAULT_CLOSED'}
    # bl_context = "view_layer"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        view_layer = context.view_layer

        layout.prop(view_layer, "material_override")
        layout.prop(view_layer, "samples")


class BPCYCLES_RENDER_PT_passes(BPCyclesButtonsPanel, Panel):
    bl_label = "Passes"
    bl_options = {'DEFAULT_CLOSED'}
    # bl_context = "view_layer"

    def draw(self, context):
        pass


class BPCYCLES_RENDER_PT_passes_data(BPCyclesButtonsPanel, Panel):
    bl_label = "Data"
    # bl_context = "view_layer"
    bl_parent_id = "BPCYCLES_RENDER_PT_passes"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        rd = scene.render
        view_layer = context.view_layer
        cycles_view_layer = view_layer.cycles

        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
        col = flow.column()
        col.prop(view_layer, "use_pass_combined")
        col = flow.column()
        col.prop(view_layer, "use_pass_z")
        col = flow.column()
        col.prop(view_layer, "use_pass_mist")
        col = flow.column()
        col.prop(view_layer, "use_pass_normal")
        col = flow.column()
        col.prop(view_layer, "use_pass_vector")
        col.active = not rd.use_motion_blur
        col = flow.column()
        col.prop(view_layer, "use_pass_uv")
        col = flow.column()
        col.prop(view_layer, "use_pass_object_index")
        col = flow.column()
        col.prop(view_layer, "use_pass_material_index")

        layout.separator()

        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
        col = flow.column()
        col.prop(cycles_view_layer, "denoising_store_passes", text="Denoising Data")
        col = flow.column()
        col.prop(cycles_view_layer, "pass_debug_render_time", text="Render Time")

        layout.separator()

        layout.prop(view_layer, "pass_alpha_threshold")


class BPCYCLES_RENDER_PT_passes_light(BPCyclesButtonsPanel, Panel):
    bl_label = "Light"
    # bl_context = "view_layer"
    bl_parent_id = "BPCYCLES_RENDER_PT_passes"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        view_layer = context.view_layer
        cycles_view_layer = view_layer.cycles

        split = layout.split(factor=0.35)
        split.use_property_split = False
        split.label(text="Diffuse")
        row = split.row(align=True)
        row.prop(view_layer, "use_pass_diffuse_direct", text="Direct", toggle=True)
        row.prop(view_layer, "use_pass_diffuse_indirect", text="Indirect", toggle=True)
        row.prop(view_layer, "use_pass_diffuse_color", text="Color", toggle=True)

        split = layout.split(factor=0.35)
        split.use_property_split = False
        split.label(text="Glossy")
        row = split.row(align=True)
        row.prop(view_layer, "use_pass_glossy_direct", text="Direct", toggle=True)
        row.prop(view_layer, "use_pass_glossy_indirect", text="Indirect", toggle=True)
        row.prop(view_layer, "use_pass_glossy_color", text="Color", toggle=True)

        split = layout.split(factor=0.35)
        split.use_property_split = False
        split.label(text="Transmission")
        row = split.row(align=True)
        row.prop(view_layer, "use_pass_transmission_direct", text="Direct", toggle=True)
        row.prop(view_layer, "use_pass_transmission_indirect", text="Indirect", toggle=True)
        row.prop(view_layer, "use_pass_transmission_color", text="Color", toggle=True)

        split = layout.split(factor=0.35)
        split.use_property_split = False
        split.label(text="Subsurface")
        row = split.row(align=True)
        row.prop(view_layer, "use_pass_subsurface_direct", text="Direct", toggle=True)
        row.prop(view_layer, "use_pass_subsurface_indirect", text="Indirect", toggle=True)
        row.prop(view_layer, "use_pass_subsurface_color", text="Color", toggle=True)

        split = layout.split(factor=0.35)
        split.use_property_split = False
        split.label(text="Volume")
        row = split.row(align=True)
        row.prop(cycles_view_layer, "use_pass_volume_direct", text="Direct", toggle=True)
        row.prop(cycles_view_layer, "use_pass_volume_indirect", text="Indirect", toggle=True)

        col = layout.column(align=True)
        col.prop(view_layer, "use_pass_emit", text="Emission")
        col.prop(view_layer, "use_pass_environment")
        col.prop(view_layer, "use_pass_shadow")
        col.prop(view_layer, "use_pass_ambient_occlusion", text="Ambient Occlusion")


class BPCYCLES_RENDER_PT_passes_crypto(BPCyclesButtonsPanel, Panel):
    bl_label = "Cryptomatte"
    # bl_context = "view_layer"
    bl_parent_id = "BPCYCLES_RENDER_PT_passes"

    def draw(self, context):
        import _cycles

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        cycles_view_layer = context.view_layer.cycles

        row = layout.row(align=True)
        row.use_property_split = False
        row.prop(cycles_view_layer, "use_pass_crypto_object", text="Object", toggle=True)
        row.prop(cycles_view_layer, "use_pass_crypto_material", text="Material", toggle=True)
        row.prop(cycles_view_layer, "use_pass_crypto_asset", text="Asset", toggle=True)

        layout.prop(cycles_view_layer, "pass_crypto_depth", text="Levels")

        row = layout.row(align=True)
        row.active = use_cpu(context)
        row.prop(cycles_view_layer, "pass_crypto_accurate", text="Accurate Mode")


class BPCYCLES_RENDER_PT_passes_debug(BPCyclesButtonsPanel, Panel):
    bl_label = "Debug"
    bl_context = "view_layer"
    bl_parent_id = "BPCYCLES_RENDER_PT_passes"

    @classmethod
    def poll(cls, context):
        import _cycles
        return _cycles.with_cycles_debug

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        cycles_view_layer = context.view_layer.cycles

        layout.prop(cycles_view_layer, "pass_debug_bvh_traversed_nodes")
        layout.prop(cycles_view_layer, "pass_debug_bvh_traversed_instances")
        layout.prop(cycles_view_layer, "pass_debug_bvh_intersections")
        layout.prop(cycles_view_layer, "pass_debug_ray_bounces")


class BPCYCLES_RENDER_PT_denoising(BPCyclesButtonsPanel, Panel):
    bl_label = "Denoising"
    # bl_context = "view_layer"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        view_layer = context.view_layer
        cycles_view_layer = view_layer.cycles
        layout = self.layout

        layout.prop(cycles_view_layer, "use_denoising", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        view_layer = context.view_layer
        cycles_view_layer = view_layer.cycles

        split = layout.split()
        split.active = cycles_view_layer.use_denoising

        layout = layout.column(align=True)
        layout.prop(cycles_view_layer, "denoising_radius", text="Radius")
        layout.prop(cycles_view_layer, "denoising_strength", slider=True, text="Strength")
        layout.prop(cycles_view_layer, "denoising_feature_strength", slider=True, text="Feature Strength")
        layout.prop(cycles_view_layer, "denoising_relative_pca")

        layout.separator()

        split = layout.split(factor=0.5)
        split.active = cycles_view_layer.use_denoising or cycles_view_layer.denoising_store_passes

        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text="Diffuse")

        row = split.row(align=True)
        row.use_property_split = False
        row.prop(cycles_view_layer, "denoising_diffuse_direct", text="Direct", toggle=True)
        row.prop(cycles_view_layer, "denoising_diffuse_indirect", text="Indirect", toggle=True)

        split = layout.split(factor=0.5)
        split.active = cycles_view_layer.use_denoising or cycles_view_layer.denoising_store_passes

        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text="Glossy")

        row = split.row(align=True)
        row.use_property_split = False
        row.prop(cycles_view_layer, "denoising_glossy_direct", text="Direct", toggle=True)
        row.prop(cycles_view_layer, "denoising_glossy_indirect", text="Indirect", toggle=True)

        split = layout.split(factor=0.5)
        split.active = cycles_view_layer.use_denoising or cycles_view_layer.denoising_store_passes

        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text="Transmission")

        row = split.row(align=True)
        row.use_property_split = False
        row.prop(cycles_view_layer, "denoising_transmission_direct", text="Direct", toggle=True)
        row.prop(cycles_view_layer, "denoising_transmission_indirect", text="Indirect", toggle=True)

        split = layout.split(factor=0.5)
        split.active = cycles_view_layer.use_denoising or cycles_view_layer.denoising_store_passes

        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text="Subsurface")

        row = split.row(align=True)
        row.use_property_split = False
        row.prop(cycles_view_layer, "denoising_subsurface_direct", text="Direct", toggle=True)
        row.prop(cycles_view_layer, "denoising_subsurface_indirect", text="Indirect", toggle=True)


class BPCYCLES_PT_post_processing(BPCyclesButtonsPanel, Panel):
    bl_label = "Post Processing"
    bl_options = {'DEFAULT_CLOSED'}
    # bl_context = "output"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        rd = context.scene.render

        col = layout.column(align=True)
        col.prop(rd, "use_compositing")
        col.prop(rd, "use_sequencer")

        layout.prop(rd, "dither_intensity", text="Dither", slider=True)


class BPCYCLES_CAMERA_PT_dof(BPCyclesButtonsPanel, Panel):
    bl_label = "Depth of Field"
    # bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'CAMERA' and BPCyclesButtonsPanel.poll(context)

    def draw_header(self, context):
        cam = context.object.data
        dof = cam.dof
        self.layout.prop(dof, "use_dof", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        cam = context.object.data
        dof = cam.dof
        layout.active = dof.use_dof

        split = layout.split()

        col = split.column()
        col.prop(dof, "focus_object", text="Focus Object")

        sub = col.row()
        sub.active = dof.focus_object is None
        sub.prop(dof, "focus_distance", text="Distance")


class BPCYCLES_CAMERA_PT_dof_aperture(BPCyclesButtonsPanel, Panel):
    bl_label = "Aperture"
    bl_parent_id = "BPCYCLES_CAMERA_PT_dof"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'CAMERA' and BPCyclesButtonsPanel.poll(context)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        cam = context.object.data
        dof = cam.dof
        layout.active = dof.use_dof
        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)

        col = flow.column()
        col.prop(dof, "aperture_fstop")
        col.prop(dof, "aperture_blades")
        col.prop(dof, "aperture_rotation")
        col.prop(dof, "aperture_ratio")


# class BPCYCLES_PT_context_material(BPCyclesButtonsPanel, Panel):
#     bl_label = ""
#     bl_context = "material"
#     bl_options = {'HIDE_HEADER'}

#     @classmethod
#     def poll(cls, context):
#         if context.active_object and context.active_object.type == 'GPENCIL':
#             return False
#         else:
#             return (context.material or context.object) and CyclesButtonsPanel.poll(context)

#     def draw(self, context):
#         layout = self.layout

#         mat = context.material
#         ob = context.object
#         slot = context.material_slot
#         space = context.space_data

#         if ob:
#             is_sortable = len(ob.material_slots) > 1
#             rows = 1
#             if (is_sortable):
#                 rows = 4

#             row = layout.row()

#             row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=rows)

#             col = row.column(align=True)
#             col.operator("object.material_slot_add", icon='ADD', text="")
#             col.operator("object.material_slot_remove", icon='REMOVE', text="")

#             col.menu("MATERIAL_MT_context_menu", icon='DOWNARROW_HLT', text="")

#             if is_sortable:
#                 col.separator()

#                 col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
#                 col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

#             if ob.mode == 'EDIT':
#                 row = layout.row(align=True)
#                 row.operator("object.material_slot_assign", text="Assign")
#                 row.operator("object.material_slot_select", text="Select")
#                 row.operator("object.material_slot_deselect", text="Deselect")

#         split = layout.split(factor=0.65)

#         if ob:
#             split.template_ID(ob, "active_material", new="material.new")
#             row = split.row()

#             if slot:
#                 row.prop(slot, "link", text="")
#             else:
#                 row.label()
#         elif mat:
#             split.template_ID(space, "pin_id")
#             split.separator()


class BPCYCLES_OBJECT_PT_motion_blur(BPCyclesButtonsPanel, Panel):
    bl_label = "Motion Blur"
    # bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        if BPCyclesButtonsPanel.poll(context) and ob:
            if ob.type in {'MESH', 'CURVE', 'CURVE', 'SURFACE', 'FONT', 'META', 'CAMERA'}:
                return True
            if ob.instance_type == 'COLLECTION' and ob.instance_collection:
                return True
            # TODO(sergey): More duplicator types here?
        return False

    def draw_header(self, context):
        layout = self.layout

        rd = context.scene.render
        # scene = context.scene

        layout.active = rd.use_motion_blur

        ob = context.object
        cob = ob.cycles

        layout.prop(cob, "use_motion_blur", text="")

    def draw(self, context):
        layout = self.layout

        rd = context.scene.render
        # scene = context.scene

        ob = context.object
        cob = ob.cycles

        layout.active = (rd.use_motion_blur and cob.use_motion_blur)

        row = layout.row()
        if ob.type != 'CAMERA':
            row.prop(cob, "use_deform_motion", text="Deformation")
        row.prop(cob, "motion_steps", text="Steps")

def has_geometry_visibility(ob):
    return ob and ((ob.type in {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META', 'LIGHT'}) or
                    (ob.instance_type == 'COLLECTION' and ob.instance_collection))


class BPCYCLES_OBJECT_PT_visibility(BPCyclesButtonsPanel, Panel):
    bl_label = "Visibility"
    # bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return  BPCyclesButtonsPanel.poll(context) and (context.object)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        flow = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=False, align=False)
        layout = self.layout
        ob = context.object

        col = flow.column()
        col.prop(ob, "hide_viewport", text="Show in Viewports", invert_checkbox=True, toggle=False)
        col = flow.column()
        col.prop(ob, "hide_render", text="Show in Renders", invert_checkbox=True, toggle=False)
        col = flow.column()
        col.prop(ob, "hide_select", text="Selectable", invert_checkbox=True, toggle=False)

        if has_geometry_visibility(ob):
            cob = ob.cycles
            col = flow.column()
            col.prop(cob, "is_shadow_catcher")
            col = flow.column()
            col.prop(cob, "is_holdout")


class BPCYCLES_OBJECT_PT_visibility_ray_visibility(BPCyclesButtonsPanel, Panel):
    bl_label = "Ray Visibility"
    bl_parent_id = "BPCYCLES_OBJECT_PT_visibility"
    # bl_context = "object"

    @classmethod
    def poll(cls, context):
        ob = context.object
        return BPCyclesButtonsPanel.poll(context) and has_geometry_visibility(ob)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        ob = context.object
        cob = ob.cycles
        visibility = ob.cycles_visibility

        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)

        col = flow.column()
        col.prop(visibility, "camera")
        col = flow.column()
        col.prop(visibility, "diffuse")
        col = flow.column()
        col.prop(visibility, "glossy")
        col = flow.column()
        col.prop(visibility, "transmission")
        col = flow.column()
        col.prop(visibility, "scatter")

        if ob.type != 'LIGHT':
            col = flow.column()
            col.prop(visibility, "shadow")

        layout.separator()


class BPCYCLES_OBJECT_PT_visibility_culling(BPCyclesButtonsPanel, Panel):
    bl_label = "Culling"
    bl_parent_id = "BPCYCLES_OBJECT_PT_visibility"
    # bl_context = "object"

    @classmethod
    def poll(cls, context):
        ob = context.object
        return BPCyclesButtonsPanel.poll(context) and has_geometry_visibility(ob)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        cscene = scene.cycles
        ob = context.object
        cob = ob.cycles

        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)

        col = flow.column()
        col.active = scene.render.use_simplify and cscene.use_camera_cull
        col.prop(cob, "use_camera_cull")

        col = flow.column()
        col.active = scene.render.use_simplify and cscene.use_distance_cull
        col.prop(cob, "use_distance_cull")


classes = (
    BPCYCLES_PT_sampling_presets,
    BPCYCLES_PT_integrator_presets,
    BPCYCLES_RENDER_PT_sampling,
    BPCYCLES_RENDER_PT_sampling_sub_samples,
    BPCYCLES_RENDER_PT_sampling_advanced,
    BPCYCLES_RENDER_PT_sampling_total,
    BPCYCLES_RENDER_PT_subdivision,
    BPCYCLES_RENDER_PT_hair,
    BPCYCLES_RENDER_PT_volumes,
    BPCYCLES_RENDER_PT_light_paths,
    BPCYCLES_RENDER_PT_light_paths_max_bounces,
    BPCYCLES_RENDER_PT_light_paths_caustics,
    BPCYCLES_RENDER_PT_motion_blur,
    BPCYCLES_RENDER_PT_motion_blur_curve,
    BPCYCLES_RENDER_PT_film,
    BPCYCLES_RENDER_PT_film_transparency,
    BPCYCLES_RENDER_PT_film_pixel_filter,
    BPCYCLES_RENDER_PT_performance,
    BPCYCLES_RENDER_PT_performance_tiles,
    BPCYCLES_RENDER_PT_performance_acceleration_structure,
    BPCYCLES_RENDER_PT_performance_viewport,
    BPCYCLES_RENDER_PT_filter,
    BPCYCLES_RENDER_PT_override,
    BPCYCLES_RENDER_PT_passes,
    BPCYCLES_RENDER_PT_passes_data,
    BPCYCLES_RENDER_PT_passes_light,
    BPCYCLES_RENDER_PT_passes_crypto,
    BPCYCLES_RENDER_PT_passes_debug,
    BPCYCLES_RENDER_PT_denoising,
    BPCYCLES_PT_post_processing,
    BPCYCLES_CAMERA_PT_dof,
    BPCYCLES_CAMERA_PT_dof_aperture,
    BPCYCLES_OBJECT_PT_motion_blur,
    BPCYCLES_OBJECT_PT_visibility,
    BPCYCLES_OBJECT_PT_visibility_ray_visibility,
    BPCYCLES_OBJECT_PT_visibility_culling
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                