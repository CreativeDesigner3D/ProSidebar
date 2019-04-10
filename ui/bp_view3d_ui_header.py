import bpy
from bpy.types import Header, Menu, Panel

class DrawMenu(bpy.types.Menu):
    bl_label = "Draw"
    bl_idname = "OBJECT_MT_draw_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator('bp.draw_plane')
        layout.label(text="TODO: Draw Cube")
        layout.label(text="TODO: Draw Lamp")
        layout.label(text="TODO: Draw Particle")

class LibraryMenu(bpy.types.Menu):
    bl_label = "Library"
    bl_idname = "OBJECT_MT_library_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator('bp.object_library',text="Show Library")

def draw_item(self, context):
    layout = self.layout
    layout.menu(DrawMenu.bl_idname)
    layout.menu(LibraryMenu.bl_idname)
            
classes = (
    DrawMenu,
    LibraryMenu,
)

register, unregister = bpy.utils.register_classes_factory(classes)

bpy.types.VIEW3D_MT_editor_menus.append(draw_item)

if __name__ == "__main__":
    register()                    