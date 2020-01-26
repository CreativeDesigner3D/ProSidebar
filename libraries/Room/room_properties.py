import bpy

class RoomLibrary_PT_library_settings(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Library"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 18

    def draw(self, context):
        layout = self.layout
        layout.label(text="Room Library Settings")

bpy.utils.register_class(RoomLibrary_PT_library_settings)