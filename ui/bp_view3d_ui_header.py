import bpy
from bpy.types import Header, Menu, Panel

class InterfaceMenu(bpy.types.Menu):
    bl_label = "Interface"
    bl_idname = "VIEW_MT_interface_menu"

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

def draw_item(self, context):
    layout = self.layout
    layout.menu(InterfaceMenu.bl_idname)
            
classes = (
    InterfaceMenu,
)

register, unregister = bpy.utils.register_classes_factory(classes)

bpy.types.VIEW3D_MT_editor_menus.append(draw_item)

if __name__ == "__main__":
    register()                    