import bpy
from bpy.types import Header, Menu, Operator, UIList, PropertyGroup
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       BoolVectorProperty,
                       PointerProperty,
                       EnumProperty,
                       CollectionProperty)
import os
from ..bp_lib import bp_unit

class bp_material_OT_delete_material(Operator):
    bl_idname = "bp_material.delete_material"
    bl_label = "Delete Material"
    bl_description = "This will delete the material"
    bl_options = {'UNDO'}

    material_name: StringProperty(name="Material Name")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.material_name in bpy.data.materials:
            mat = bpy.data.materials[self.material_name]
            bpy.data.materials.remove(mat,do_unlink=True)
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Are you sure you want to delete the material?")  
        layout.label(text="Material Name: " + self.material_name)


class bp_material_OT_create_material_from_image(Operator):
    """Creates a new material from an image"""
    bl_idname = "bp_material.create_material_from_image"
    bl_label = "Create Material From Image"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def draw(self, context):
        self.layout.operator('file.select_all_toggle')  

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        file_path, file_name = os.path.split(self.filepath)
        filename , ext = os.path.splitext(file_name)    
        new_image = bpy.data.images.load(self.filepath)
        
        material = bpy.data.materials.new(filename)
        material.use_nodes = True
        material.node_tree.nodes.clear()

        output = material.node_tree.nodes.new("ShaderNodeOutputMaterial")
        output.location = (0,0)
        
        princ = material.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
        princ.location = (-300,0)        

        texture = material.node_tree.nodes.new("ShaderNodeTexImage")
        texture.image = new_image
        texture.location = (-600,0)  

        mapping = material.node_tree.nodes.new("ShaderNodeMapping")
        mapping.location = (-1000,0)
 
        texcord = material.node_tree.nodes.new("ShaderNodeTexCoord")
        texcord.location = (-1200,0)

        new_links = material.node_tree.links.new
        new_links(output.inputs[0], princ.outputs[0])
        new_links(princ.inputs[0], texture.outputs[0]) 
        new_links(texture.inputs[0], mapping.outputs[0]) 
        new_links(mapping.inputs[0], texcord.outputs[0]) 

        return {'FINISHED'}       

classes = (
    bp_material_OT_delete_material,
    bp_material_OT_create_material_from_image
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()               