import bpy
from bpy.types import (
        Operator,
        Panel,
        UIList,
        PropertyGroup,
        AddonPreferences,
        )
from bpy.props import (
        StringProperty,
        BoolProperty,
        IntProperty,
        CollectionProperty,
        BoolVectorProperty,
        PointerProperty,
        FloatProperty,
        )
import os

class WORLD_OT_delete_world(Operator):
    bl_idname = "bp_world.delete_world"
    bl_label = "Delete World"
    bl_description = "This will delete the world"
    bl_options = {'UNDO'}

    world_name: StringProperty(name="World Name")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.world_name in bpy.data.worlds:
            wrl = bpy.data.worlds[self.world_name]
            bpy.data.worlds.remove(wrl,do_unlink=True)
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label("Are you sure you want to delete the world?")
        layout.label("World Name: " + self.world_name)

class WORLD_OT_create_world_from_hdr(Operator):
    """Creates a New World from a HDR"""
    bl_idname = "bp_world.create_new_world_from_hdr"
    bl_label = "Create New World From HDR"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        file_path, file_name = os.path.split(self.filepath)
        filename , ext = os.path.splitext(file_name)        
        
        world = bpy.data.worlds.new(filename)
        world.use_nodes = True
        world.node_tree.nodes.clear()
        
        context.scene.world = world
        new_image = bpy.data.images.load(self.filepath)

        output = world.node_tree.nodes.new("ShaderNodeOutputWorld")
        output.location = (0,0)
        
        mix_shader = world.node_tree.nodes.new("ShaderNodeMixShader")
        mix_shader.location = (-200,0)
        
        background = world.node_tree.nodes.new("ShaderNodeBackground")
        background.location = (-400,0)
        
        background_2 = world.node_tree.nodes.new("ShaderNodeBackground")
        background_2.location = (-400,-200)        
        
        light_path = world.node_tree.nodes.new("ShaderNodeLightPath")
        light_path.location = (-400,400)        
        
        #ENVIRONMENT LIGHTING
        math_add = world.node_tree.nodes.new("ShaderNodeMath")
        math_add.name = "ADD"
        math_add.operation = 'ADD'
        math_add.location = (-600,-300)
         
        #SHADOWS
        math_multiply = world.node_tree.nodes.new("ShaderNodeMath")
        math_multiply.name = "MULTIPLY"
        math_multiply.operation = 'MULTIPLY'
        math_multiply.inputs[1].default_value = 1     
        math_multiply.location = (-800,-300) 
        
        texture = world.node_tree.nodes.new("ShaderNodeTexEnvironment")
        texture.image = new_image
        texture.location = (-1000,0)

        mapping = world.node_tree.nodes.new("ShaderNodeMapping")
        mapping.location = (-1500,0)
 
        texcord = world.node_tree.nodes.new("ShaderNodeTexCoord")
        texcord.location = (-1700,0)
        
        new_links = world.node_tree.links.new
        new_links(output.inputs[0], mix_shader.outputs[0])
        new_links(mix_shader.inputs[0], light_path.outputs[0]) 
        new_links(mix_shader.inputs[2], background.outputs[0])
        new_links(mix_shader.inputs[1], background_2.outputs[0])  
        new_links(background_2.inputs[1], math_add.outputs[0])  
        new_links(math_add.inputs[0], math_multiply.outputs[0]) 
        new_links(math_multiply.inputs[0], texture.outputs[0]) 
        new_links(background_2.inputs[0], texture.outputs[0]) 
        new_links(background.inputs[0], texture.outputs[0])     
        new_links(texture.inputs[0], mapping.outputs[0])
        new_links(mapping.inputs[0], texcord.outputs[0])
        
        return {'FINISHED'}

class WORLD_OT_create_sky_world(Operator):
    """Creates a New Sky World"""
    bl_idname = "bp_world.create_sky_world"
    bl_label = "Create Sky World"

    def execute(self, context):
        world = bpy.data.worlds.new("Sky")
        world.use_nodes = True
        world.node_tree.nodes.clear()
        
        context.scene.world = world

        output = world.node_tree.nodes.new("ShaderNodeOutputWorld")
        output.location = (0,0)
        
        background = world.node_tree.nodes.new("ShaderNodeBackground")
        background.location = (-200,0)        
        
        sky = world.node_tree.nodes.new("ShaderNodeTexSky")
        sky.location = (-400,0)

        new_links = world.node_tree.links.new
        new_links(output.inputs[0], background.outputs[0])
        new_links(background.inputs[0], sky.outputs[0]) 

        return {'FINISHED'}

class WORLD_OT_open_world_editor(bpy.types.Operator):
    bl_idname = "bp_world.open_world_editor"
    bl_label = "Open World Editor"
        
    def execute(self, context):
        bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        for window in context.window_manager.windows:
            if len(window.screen.areas) == 1 and window.screen.areas[0].type == 'PREFERENCES':
                window.screen.areas[0].type = 'NODE_EDITOR'
                for space in window.screen.areas[0].spaces:
                    if space.type == 'NODE_EDITOR':
                        space.shader_type = 'WORLD'
                        
        return {'FINISHED'} 

classes = (
    WORLD_OT_delete_world,
    WORLD_OT_create_world_from_hdr,
    WORLD_OT_create_sky_world,
    WORLD_OT_open_world_editor,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()        