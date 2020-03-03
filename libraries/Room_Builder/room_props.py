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
from .bp_lib import bp_types, bp_unit, bp_utils

class Room_Scene_Props(PropertyGroup):
    room_tabs: EnumProperty(name="Room Tabs",
                            items=[('ROOM_SETTINGS',"Room Settings","Show the Room Settings"),
                                   ('ROOM_TOOLS',"Room Tools","Show the Room Tools")],
                            default='ROOM_SETTINGS')

    wall_height: FloatProperty(name="Wall Height",default=bp_unit.inch(96),subtype='DISTANCE')
    wall_thickness: FloatProperty(name="Wall Thickness",default=bp_unit.inch(6),subtype='DISTANCE')

    def draw(self,layout):
        row = layout.row(align=True)
        row.prop_enum(self, "room_tabs", 'ROOM_SETTINGS', icon='PROPERTIES', text="Settings") 
        row.prop_enum(self, "room_tabs", 'ROOM_TOOLS', icon='MODIFIER_ON', text="Tools") 

        if self.room_tabs == 'ROOM_SETTINGS':
            box = layout.box()
            box.label(text="Default Room Size",icon='MOD_BUILD')

            row = box.row()
            row.label(text="Default Wall Height")
            row.prop(self,'wall_height',text="")

            row = box.row()
            row.label(text="Default Wall Thickness")
            row.prop(self,'wall_thickness',text="")

        if self.room_tabs == 'ROOM_TOOLS':
            col = layout.column(align=True)

            box = col.box()
            box.label(text="General Room Tools",icon='MOD_BUILD')   
            box.operator('room.draw_molding',text="Auto Add Base Molding")
            box.operator('room.draw_molding',text="Auto Add Crown Molding")              
            box.operator('room.draw_molding',text="Add Floor")

            box = col.box()
            box.label(text="Room Lighting Tools",icon='MOD_BUILD')  
            box.operator('room.draw_molding',text="Add Room Light")

            box = col.box()
            box.label(text="2D Drawing Tools",icon='MOD_BUILD')  
            box.operator('room.draw_molding',text="Generate 2D View Scenes")      
            box.operator('room.draw_molding',text="Show Dimensions")

    @classmethod
    def register(cls):
        bpy.types.Scene.room = PointerProperty(
            name="Room Props",
            description="Room Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.room

bpy.utils.register_class(Room_Scene_Props)

# classes = (
#     Room_Scene_Props,
# )

# register, unregister = bpy.utils.register_classes_factory(classes)        