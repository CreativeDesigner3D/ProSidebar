import bpy
from bpy.types import Header, Menu, Operator, PropertyGroup, Panel

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       BoolVectorProperty,
                       PointerProperty,
                       CollectionProperty,
                       EnumProperty)


class Mesh_Hook(PropertyGroup):
    pass
    #obj = PointerTOEmptyObject


class Assembly:

    bp_obj = None
    prompt_obj = None

    #mesh_hooks = CollectionProperty(type=Mesh_Hook,name="Mesh Hooks")
