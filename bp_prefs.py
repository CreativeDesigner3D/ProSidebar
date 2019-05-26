import bpy
from bpy.types import AddonPreferences

class BlenderPro_Pref(AddonPreferences):
    bl_idname = __name__

    library_path: bpy.props.StringProperty(
        name="Library path",
        subtype="DIR_PATH",
        description="Absolute path to library folder",
        default=""
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'library_path')

classes = (
    BlenderPro_Pref,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()        