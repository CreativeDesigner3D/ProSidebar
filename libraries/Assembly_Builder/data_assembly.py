from .bp_lib import bp_types

class Assembly(bp_types.Assembly):
    show_in_library = True
    category_name = "Assemblies"

    def draw_door(self):
        self.create_assembly("Assembly")
        self.obj_bp["IS_ASSEMBLY_BP"] = True

        self.obj_x.location.x = bp_unit.inch(24) #Length
        self.obj_y.location.y = bp_unit.inch(34) #Depth
        self.obj_z.location.z = bp_unit.inch(24)        