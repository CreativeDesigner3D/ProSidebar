import bpy

def draw_assembly_properties(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_AREA'
    obj = context.object
    if obj and "PROMPT_ID" in obj and obj["PROMPT_ID"] != "":
        layout.operator(obj["PROMPT_ID"],icon='SETTINGS')
        layout.separator()
    if obj and "MENU_ID" in obj and obj["MENU_ID"] != "":
        layout.operator('INVOKE_DEFAULT',obj["MENU_ID"],icon='SETTINGS')
        layout.separator()   

def register():
    bpy.types.VIEW3D_MT_object_context_menu.prepend(draw_assembly_properties)

def unregister():
    bpy.types.VIEW3D_MT_object_context_menu.remove(draw_assembly_properties)