from .bp_lib import bp_types, bp_unit

class Assembly(bp_types.Assembly):
    show_in_library = True
    category_name = "Assemblies"
    # placement_id = "assembly.assembly_prompts"
    prompt_id = "assembly.assembly_prompts"

    def draw(self):
        self.create_assembly("Assembly")
        self.obj_bp["IS_ASSEMBLY_BP"] = True
        self.obj_bp["PROMPT_ID"] = "assembly.assembly_prompts"
        self.obj_x["PROMPT_ID"] = "assembly.assembly_prompts"
        self.obj_y["PROMPT_ID"] = "assembly.assembly_prompts"
        self.obj_z["PROMPT_ID"] = "assembly.assembly_prompts"
        self.obj_x.location.x = bp_unit.inch(24) #Length
        self.obj_y.location.y = bp_unit.inch(34) #Depth
        self.obj_z.location.z = bp_unit.inch(24)        