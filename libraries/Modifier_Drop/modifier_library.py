from .bp_lib import bp_types

class Array(bp_types.Assembly):
    show_in_library = True
    category_name = "Modifiers"
    placement_id = "modifier.drop_modifier"
    prompt_id = "modifier.prompts"
    
    def add_modifier(self,obj):
        mod = obj.modifiers.new("MD Arrary",'ARRAY')
        mod.count = 3
        mod.relative_offset_displace = (2,0,0)
    