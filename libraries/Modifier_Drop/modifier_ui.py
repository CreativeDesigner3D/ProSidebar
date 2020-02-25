import bpy

class Modifier_PT_library_settings(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Library"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 18

    def draw(self, context):
        layout = self.layout
        # props = room_utils.get_room_scene_props(context)
        # props.draw(layout)

class Modifier_OT_prompts(bpy.types.Operator):
    bl_idname = "modifier.prompts"
    bl_label = "Modifier Prompts"

    obj = None

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        self.obj = context.object
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.label(text=self.obj.name)

bpy.utils.register_class(Modifier_PT_library_settings)
bpy.utils.register_class(Modifier_OT_prompts)        