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

from ..bp_props import prompt_types

#TODO: IMPLEMENT CALCULATORS
#TODO: IMPLEMENT EASY WAY TO ADD VARS FOR DRIVERS FROM PROMPTS
#TODO: IMPLEMENT EDIT PROMPT INTERFACE TO CHANGE PROMPT TYPE, RENAME, TAB INDEX 
#TODO: IMPLEMENT WAY TO ADD COMBOBOX ITEMS
#TODO: IMPLEMENT BETTER INTERFACE FOR VIEWING PROMPTS
#TODO: FIND WAY TO EXTEND RIGHT CLICK PROPERTIES
#TODO: IMPLEMENT PROMPTS FOR WORLDS, SCENES, MATERIALS, COLLECTIONS
#TODO: IMPLEMENT TABS

class OPS_add_main_tab(Operator):
    bl_idname = "fd_prompts.add_main_tab"
    bl_label = "Add Main Tab"
    bl_options = {'UNDO'}
    
    tab_name: StringProperty(name="Tab Name",default="New Tab")
    obj: PointerProperty(name="Object",type=bpy.types.Object)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        self.obj.prompts.add_tab(self.tab_name)
        context.area.tag_redraw()
        return {'FINISHED'}

    def invoke(self,context,event):
        self.tab_name = "New Tab"
        counter = 1
        while self.tab_name + " " + str(counter) in self.obj.prompts.tabs:
            counter += 1
        self.tab_name = self.tab_name + " " + str(counter)
            
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,"tab_name")  

class OPS_add_prompt(Operator):
    bl_idname = "bp_prompts.add_prompt"
    bl_label = "Add Prompt"
    bl_options = {'UNDO'}
    
    data_type: StringProperty(name="Data Type",default="")
    data_name: StringProperty(name="Data Name",default="") #WHY DON"T POINTERS WORK?

    prompt_name: StringProperty(name="Prompt Name",default="New Prompt")
    prompt_type: EnumProperty(name="Prompt Type",items=prompt_types)
    # the_obj = PointerProperty(name="Object",type=bpy.types.Object) #WHY CANNOT I USE POINTER PROPERTY

    @classmethod
    def poll(cls, context):
        return True

    def get_data(self,context):
        if self.data_type == 'OBJECT':
            if self.data_name in bpy.data.objects:
                return bpy.data.objects[self.data_name]
            else:
                return context.object
        if self.data_type == 'WORLD':
            return context.scene.world
        if self.data_type == 'COLLECTION':
            if self.data_name in bpy.data.collections:
                return bpy.data.collections[self.data_name]
            else:
                return context.view_layer.active_layer_collection.collection

    def execute(self, context):
        data = self.get_data(context)
        print("PROMPT DATA",data)
        if data:        
            data.prompt_page.add_prompt(self.prompt_type,self.prompt_name)
        context.area.tag_redraw()
        return {'FINISHED'}

    def invoke(self,context,event):
        data = self.get_data(context)
        if data:
            self.prompt_name = "New Prompt"
            counter = 1
            while self.prompt_name + " " + str(counter) in data.prompt_page.prompts:
                counter += 1
            self.prompt_name = self.prompt_name + " " + str(counter)
                
            wm = context.window_manager
            return wm.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,"prompt_name")
        layout.prop(self,"prompt_type")

classes = (
    OPS_add_main_tab,
    OPS_add_prompt
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
