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
        EnumProperty,
        )

class Assembly_Scene_Props(PropertyGroup):
    assembly_tabs: EnumProperty(name="Assembly Tabs",
                                items=[('MAIN',"Main","Show the Main Properties"),
                                       ('PROMPTS',"Prompts","Show the Prompts"),
                                       ('OBJECTS',"Objects","Show the Objects"),
                                       ('LOGIC',"Logic","Show the Assembly Logic")],
                                default='MAIN')
    
    @classmethod
    def register(cls):
        bpy.types.Scene.assembly = PointerProperty(
            name="Assembly Props",
            description="These are the Assembly Props",
            type=cls,
        )

classes = (
    Assembly_Scene_Props,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
