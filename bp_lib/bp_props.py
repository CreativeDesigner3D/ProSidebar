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


def update_scene_selection(self,context):
    pass
    #TODO: Figure out how to change scene
    # context.scene = bpy.data.scenes[self.selected_scene_index] 
    # if context.screen.scene.outliner.selected_scene_index != self.selected_scene_index:
    #     context.screen.scene.outliner.selected_scene_index = self.selected_scene_index

def update_object_selection(self,context):
    if self.selected_object_index < len(context.scene.objects):
        bpy.ops.object.select_all(action = 'DESELECT')
        obj = context.scene.objects[self.selected_object_index]
        obj.select_set(True)
        context.view_layer.objects.active = obj

def update_world_selection(self,context):
    if self.selected_world_index <= len(bpy.data.worlds) - 1:
        world = bpy.data.worlds[self.selected_world_index]
        context.scene.world = world  

class BP_Scene_Props(PropertyGroup):
    selected_scene_index: IntProperty(name="Selected Scene Index", default=0, update = update_scene_selection)
    selected_object_index: IntProperty(name="Selected Object Index", default=0, update = update_object_selection)
    selected_world_index: IntProperty(name="Selected World Index", default=0, update = update_world_selection)
    selected_material_index: IntProperty(name="Selected Material Index", default=0)
    
    object_tabs: bpy.props.EnumProperty(name="Object Tabs",
                                        items=[('MAIN',"Main","Show the Scene Options"),
                                               ('MATERIAL',"Material","Show the Material Options"),
                                               ('MODIFIERS',"Modifiers","Show the Modifiers"),
                                               ('LOGIC',"Logic","Show the Drivers")],
                                        default='MAIN')
    
    @classmethod
    def register(cls):
        bpy.types.Scene.bp_props = PointerProperty(
            name="BP Props",
            description="Blender Pro Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.bp_props

class BP_Collection_Props(PropertyGroup):
    selected_object_index: IntProperty(name="Select Object Index", default=False)
    assembly_tabs: bpy.props.EnumProperty(name="Assembly Tabs",
                                          items=[('MAIN',"Main","Show the Scene Options"),
                                                 ('PROMPTS',"Prompts","Show the Assembly Prompts"),
                                                 ('OBJECTS',"Objects","Show the Objects"),
                                                 ('LOGIC',"Logic","Show the Driver Logic")],
                                          default='MAIN')
    @classmethod
    def register(cls):
        bpy.types.Collection.bp_props = PointerProperty(name="BP Props",description="Blender Pro Props",type=cls)
        
    @classmethod
    def unregister(cls):
        del bpy.types.Collection.bp_props

class BP_Object_Props(PropertyGroup):
    show_driver_debug_info: BoolProperty(name="Show Driver Debug Info", default=False)

    @classmethod
    def register(cls):
        bpy.types.Object.bp_props = PointerProperty(name="BP Props",description="Blender Pro Props",type=cls)
        
    @classmethod
    def unregister(cls):
        del bpy.types.Object.bp_props

classes = (
    BP_Scene_Props,
    BP_Collection_Props,
    BP_Object_Props,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
