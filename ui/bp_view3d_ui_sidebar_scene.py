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

class VIEW3D_PT_scenes(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Scene"
    bl_category = "Scene"
    bl_options = {'HIDE_HEADER'}
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.scale_y = 1.3
        row.template_ID(context.window, "scene", new="scene.new", unlink="scene.delete")

        # box = layout.box()
        # box.label(text="Scenes",icon='SCENE_DATA')

        # if len(bpy.data.scenes) > 0:
        #     box.template_list("SCENE_UL_scenes", "", bpy.data, "scenes", context.scene.bp_props, "selected_scene_index", rows=4)


class VIEW3D_PT_scenes_units(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Units"
    bl_category = "Scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='',icon='DRIVER_DISTANCE')

    def draw(self, context):
        layout = self.layout

        unit = context.scene.unit_settings

        layout.use_property_split = False
        layout.use_property_decorate = False

        layout.prop(unit, "system",expand=True)

        col = layout.column()
        col.enabled = unit.system != 'NONE'
        col.prop(unit, "scale_length")
        col.prop(unit, "use_separate")

        col = layout.column()
        col.prop(unit, "system_rotation", text="Rotation")
        subcol = col.column()
        subcol.enabled = unit.system != 'NONE'
        subcol.prop(unit, "length_unit", text="Length")
        subcol.prop(unit, "mass_unit", text="Mass")
        subcol.prop(unit, "time_unit", text="Time")

class VIEW3D_PT_scenes_audio(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Audio"
    bl_category = "Scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='',icon='OUTLINER_OB_SPEAKER')

    def draw(self, context):
        layout = self.layout
        # layout.use_property_split = True

        scene = context.scene
        rd = context.scene.render
        ffmpeg = rd.ffmpeg
        strip = None
        sound = None
        if context.scene.sequence_editor is None:
            context.scene.sequence_editor_create()

        for sequence in context.scene.sequence_editor.sequences:
            if sequence.type == 'SOUND':
                strip = sequence
                sound = strip.sound

        if sound is not None:
            layout.prop(sound, "filepath", text="")

            row = layout.row()
            if sound.packed_file:
                row.operator("sound.unpack", icon='PACKAGE', text="Unpack")
            else:
                row.operator("sound.pack", icon='UGLYPACKAGE', text="Pack")

            row.prop(sound, "use_memory_cache")

            # layout.prop(sound, "use_mono")

        # if st.waveform_display_type == 'DEFAULT_WAVEFORMS':
        #     layout.prop(strip, "show_waveform")

            box = layout.box()
            box.label(text="Audio Settings")

            col = box.column(align=True)
            row = col.row(align=True)
            row.prop(strip, "volume",text="Volume")    
            row.prop(strip, "pitch",text="Pitch")
            row.prop(strip, "pan",text="Pan")

            row = box.row(align=True)
            row.label(text="Trim (Hard):")
            row.prop(strip, "animation_offset_start", text="Start")
            row.prop(strip, "animation_offset_end", text="End")

            row = box.row(align=True)
            row.label(text="Trim (Soft):")
            row.prop(strip, "frame_offset_start", text="Start")
            row.prop(strip, "frame_offset_end", text="End")
        else:
            layout.operator('bp_scene.add_audio')

class SCENE_UL_scenes(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name,icon='SCENE_DATA')
        layout.operator('bp_scene.delete_scene',icon='X',text="",emboss=False).scene_name = item.name


classes = (
    VIEW3D_PT_scenes,
    VIEW3D_PT_scenes_units,
    VIEW3D_PT_scenes_audio,
    SCENE_UL_scenes,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()        