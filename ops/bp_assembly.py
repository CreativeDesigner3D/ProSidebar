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
from ..bp_lib import bp_types, bp_utils

class ASSEMBLY_OT_create_new_assembly(Operator):
    bl_idname = "bp_assembly.create_new_assembly"
    bl_label = "Create New Assembly"
    bl_description = "This will create a new assembly"
    bl_options = {'UNDO'}

    assembly_name: StringProperty(name="Assembly Name",default="New Assembly")


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        assembly = bp_types.Assembly()
        assembly.create_assembly()
        assembly.obj_x.location.x = 1
        assembly.obj_y.location.y = 1
        assembly.obj_z.location.z = 1
        assembly.obj_bp.select_set(True)
        context.view_layer.objects.active = assembly.obj_bp
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Enter the name of the assembly to add.")
        layout.prop(self,'assembly_name')

class ASSEMBLY_OT_add_object(Operator):
    bl_idname = "bp_assembly.add_object"
    bl_label = "Add Object to Assembly"
    bl_description = "This will add a new object to the assembly"
    bl_options = {'UNDO'}

    assembly_name: StringProperty(name="Assembly Name",default="New Assembly")

    object_name: StringProperty(name="Object Name",default="New Object")
    object_type: bpy.props.EnumProperty(name="Object Type",
                                        items=[('EMPTY',"Empty","Add an Empty Object"),
                                               ('MESH',"Mesh","Add an Mesh Object"),
                                               ('CURVE',"Curve","Add an Curve Object"),
                                               ('LIGHT',"Light","Add an Light Object")],
                                        default='EMPTY')
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        assembly = bp_types.Assembly(context.view_layer.active_layer_collection.collection)
        if self.object_type == 'EMPTY':
            assembly.add_empty("New Empty")

        if self.object_type == 'MESH':
            obj_mesh = bp_utils.create_cube_mesh(self.object_name,(assembly.obj_x.location.x,
                                                                   assembly.obj_y.location.y,
                                                                   assembly.obj_z.location.z))
            
            assembly.add_object(obj_mesh)

            # MAKE NORMALS CONSISTENT
            context.view_layer.objects.active = obj_mesh
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.editmode_toggle()

        if self.object_type == 'CURVE':
            pass           
        if self.object_type == 'LIGHT':
            pass
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'object_type',expand=True)
        layout.prop(self,'object_name')

class ASSEMBLY_OT_connect_mesh_to_hooks_in_assembly(Operator):
    bl_idname = "bp_assembly.connect_meshes_to_hooks_in_assembly"
    bl_label = "Connect Mesh to Hooks In Assembly"
    bl_options = {'UNDO'}
    
    obj_name: StringProperty(name="Object Name")
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        obj = bpy.data.objects[self.obj_name]
        coll = bp_utils.get_assembly_collection(obj)

        hooklist = []
        for child in coll.objects:
            if child.type == 'EMPTY' and 'obj_prompts' not in child:
                hooklist.append(child)
        
        if obj.mode == 'EDIT':
            bpy.ops.object.editmode_toggle()
        
        bp_utils.apply_hook_modifiers(context,obj)
        for vgroup in obj.vertex_groups:
            for hook in hooklist:
                if hook.name == vgroup.name:
                    bp_utils.hook_vertex_group_to_object(obj,vgroup.name,hook)

        obj.lock_location = (True,True,True)
                
        return {'FINISHED'}

class ASSEMBLY_OT_create_assembly_script(Operator):
    bl_idname = "bp_assembly.create_assembly_script"
    bl_label = "Create Assembly Script"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        obj = context.object
        coll = bp_utils.get_assembly_collection(obj)
        assembly = bp_types.Assembly(coll)

        #Create New Script
        text = bpy.data.texts.new(coll.name)

        #Add Imports
        text.write('import bpy\n')
        #Figure out how to import bp_types
                
        #Add Class Def
        text.write('class ' + coll.name + '(bp_types.Assembly):\n')
        text.write('    def draw(self):\n')
        text.write('    self.create_assembly()\n')

        #Add Prompts
        for prompt in assembly.obj_prompts.prompt_page.prompts:
            pass

        #Add Empty Objects Except Built-in Assembly Objects
        #for obj in assembly.empty_objs:
        for obj in assembly.obj_bp.children:
            if obj.type == 'EMPTY':
                pass #Assign Drivers and Constraints

        #Add Mesh Objects This needs to be done after empties for hooks
        #for obj in assembly.mesh_objs:
        for obj in assembly.obj_bp.children:
            pass
        return {'FINISHED'}

classes = (
    ASSEMBLY_OT_create_new_assembly,
    ASSEMBLY_OT_add_object,
    ASSEMBLY_OT_connect_mesh_to_hooks_in_assembly,
    ASSEMBLY_OT_create_assembly_script
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()