import bpy
from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        UIList,
        )

class VIEW3D_PT_worlds(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "World"
    bl_category = "World"
    bl_options = {'HIDE_HEADER'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        world = scene.world
        view = context.space_data
        
        row = layout.row()
        row.scale_y = 1.3        
        row.menu('VIEW3D_MT_add_world',icon='WORLD')
        
        if len(bpy.data.worlds) > 0:
            layout.template_list("BP_UL_worlds", "", bpy.data, "worlds", scene.bp_props, "selected_world_index", rows=4)
        layout.prop(world,'name')
        layout.operator('bp_world.open_world_editor',text="Show Node Editor",icon='WORLD')

        # box = layout.box()
        # box.label(text="Active World Properties: " + world.name,icon='WORLD')
        
        # # box.prop(view, "show_world",text="Show World in Viewport")
        # for node in world.node_tree.nodes:
        #     if node.bl_idname == 'ShaderNodeBackground':
        #         box.prop(node.inputs[1],'default_value',text="Strength")
        #     if node.bl_idname == 'ShaderNodeMapping':
        #         box.prop(node,'rotation')


class VIEW3D_PT_world_prompts(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "World"
    bl_label = "Prompts"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if context.scene.world:
            return True
        else:
            return False

    def draw_header(self, context):
        layout = self.layout
        obj = context.object
        layout.label(text="",icon='LINENUMBERS_ON')

    def draw(self, context):
        layout = self.layout
        world = context.scene.world
        if world:
            world.prompt_page.draw_prompts(layout,'WORLD')


class VIEW3D_MT_add_world(bpy.types.Menu):
    bl_label = "Add World"

    def draw(self, context):
        layout = self.layout
        layout.operator("world.new",icon='ADD')
        layout.operator("bp_world.create_sky_world",icon='NODE_COMPOSITING')
        layout.operator("bp_world.create_new_world_from_hdr",icon='RENDER_RESULT')


class BP_UL_worlds(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name,icon='WORLD_DATA')
        if item.name == context.scene.world.name:
            layout.label(text='',icon='CHECKBOX_HLT')
        layout.operator('bp_world.delete_world',icon='X',text="",emboss=False).world_name = item.name

classes = (
    VIEW3D_PT_worlds,
    VIEW3D_MT_add_world,
    VIEW3D_PT_world_prompts,
    BP_UL_worlds,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()        