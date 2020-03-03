import bpy
import math
from .bp_lib import bp_types, bp_unit, bp_utils
import time
from . import room_types, room_utils
from . import data_parts

class Door(room_types.Door):
    show_in_library = True

    def draw_door(self):
        self.create_assembly("Door")

        boolean_overhang = self.obj_prompts.prompt_page.add_prompt('DISTANCE',"Boolean Overhang")
        boolean_overhang.set_value(bp_unit.inch(1))

        self.obj_x.location.x = bp_unit.inch(36) #Length
        self.obj_y.location.y = bp_unit.inch(6) #Depth
        self.obj_z.location.z = bp_unit.inch(70)

        length = self.obj_x.drivers.get_var('location.x','length')
        depth = self.obj_y.drivers.get_var('location.y','depth')
        height = self.obj_z.drivers.get_var('location.z','height')
        boolean_overhang_var = boolean_overhang.get_var("boolean_overhang_var")

        hole = self.add_assembly(data_parts.Cube())
        for child in hole.obj_bp.children:
            if child.type == 'MESH':
                child['IS_BOOLEAN'] = True
        hole.set_name("Hole")
        hole.loc_x(value=0)
        hole.loc_y('-boolean_overhang_var',[boolean_overhang_var])
        hole.loc_z('-boolean_overhang_var',[boolean_overhang_var])
        hole.rot_z(value=math.radians(0))
        hole.dim_x('length',[length])
        hole.dim_y('depth+(boolean_overhang_var*2)',[depth,boolean_overhang_var])
        hole.dim_z('height+boolean_overhang_var',[height,boolean_overhang_var])

        