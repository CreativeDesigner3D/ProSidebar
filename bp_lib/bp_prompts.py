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
    
#TODO: IMPLEMENT CALCULATORS
#TODO: IMPLEMENT EASY WAY TO ADD VARS FOR DRIVERS FROM PROMPTS
#TODO: IMPLEMENT EDIT PROMPT INTERFACE TO CHANGE PROMPT TYPE, RENAME, TAB INDEX 
#TODO: IMPLEMENT WAY TO ADD COMBOBOX ITEMS
#TODO: IMPLEMENT BETTER INTERFACE FOR VIEWING PROMPTS
#TODO: FIND WAY TO EXTEND RIGHT CLICK PROPERTIES
#TODO: IMPLEMENT PROMPTS FOR WORLDS, SCENES, MATERIALS, COLLECTIONS
#TODO: IMPLEMENT TABS

prompt_types = [('FLOAT',"Float","Float"),
                ('DISTANCE',"Distance","Distance"),
                ('ANGLE',"Angle","Angle"),
                ('QUANTITY',"Quantity","Quantity"),
                ('PERCENTAGE',"Percentage","Percentage"),
                ('CHECKBOX',"Checkbox","Checkbox"),
                ('COMBOBOX',"Combobox","Combobox"),
                ('TEXT',"Text","Text")]


class Combobox_Item(PropertyGroup):
    pass    
    

class Tab(PropertyGroup):
    pass    


class Prompt(PropertyGroup):
    tab_index: IntProperty(name="Tab Index")
    prompt_type: EnumProperty(name="Prompt Type",items=prompt_types)

    float_value: FloatProperty(name="Float Value")
    distance_value: FloatProperty(name="Distance Value",subtype='DISTANCE')
    angle_value: FloatProperty(name="Angle Value",subtype='ANGLE')
    quantity_value: IntProperty(name="Quantity Value",subtype='DISTANCE',min=0)
    percentage_value: FloatProperty(name="Percentage Value",subtype='PERCENTAGE',min=0,max=1)
    checkbox_value: BoolProperty(name="Checkbox Value", description="")
    text_value: StringProperty(name="Text Value", description="")

    calculator_index: IntProperty(name="Calculator Index")

    combobox_items: CollectionProperty(type=Combobox_Item, name="Tabs")
    combobox_index: IntProperty(name="Combobox Index", description="")
    combobox_columns: IntProperty(name="Combobox Columns")

    def draw(self,layout):
        row = layout.row()
        row.label(text=self.name)
        if self.prompt_type == 'FLOAT':
            row.prop(self,"float_value")
        if self.prompt_type == 'DISTANCE':
            row.prop(self,"distance_value")
        if self.prompt_type == 'ANGLE':
            row.prop(self,"angle_value")
        if self.prompt_type == 'QUANTITY':
            row.prop(self,"quantity_value")
        if self.prompt_type == 'PERCENTAGE':
            row.prop(self,"percentage_value")
        if self.prompt_type == 'CHECKBOX':
            row.prop(self,"checkbox_value")
        if self.prompt_type == 'COMBOBOX':
            row.prop(self,"combobox_index") #TODO: IMPLEMENT UI LIST
        if self.prompt_type == 'TEXT':
            row.prop(self,"text_value")


class Prompt_Page(PropertyGroup):
    tabs: CollectionProperty(type=Tab, name="Tabs")
    tab_index: IntProperty(name="Tab Index")
    prompts: CollectionProperty(type=Prompt, name="Prompts")
    
    @classmethod
    def register(cls):
        bpy.types.Object.prompt_page = PointerProperty(
            name="Prompt Page",
            description="Blender Pro Prompts",
            type=cls,
        )
        
        bpy.types.World.prompt_page = PointerProperty(
            name="Prompt Page",
            description="Blender Pro Prompts",
            type=cls,
        )

    @classmethod
    def unregister(cls):
        del bpy.types.Object.prompt_page
        del bpy.types.World.prompt_page

    def add_tab(self,name):
        tab = self.tabs.add()
        tab.name = name

    def draw_prompts(self,layout,data_type):
        layout.operator('bp_prompts.add_prompt').data_type = data_type
        for prompt in self.prompts:
            prompt.draw(layout)
    
    def add_prompt(self,prompt_type,prompt_name):
        prompt = self.prompts.add()
        prompt.prompt_type = prompt_type
        prompt.name = prompt_name
        prompt.tab_index = self.tab_index
            
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

    prompt_name: StringProperty(name="Prompt Name",default="New Prompt")
    prompt_type: EnumProperty(name="Prompt Type",items=prompt_types)
    # the_obj = PointerProperty(name="Object",type=bpy.types.Object) #WHY CANNOT I USE POINTER PROPERTY

    @classmethod
    def poll(cls, context):
        return True

    def get_data(self,context):
        if self.data_type == 'OBJECT':
            return context.object
        if self.data_type == 'WORLD':
            return context.scene.world

    def execute(self, context):
        data = self.get_data(context)
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
    Combobox_Item,
    Tab,
    Prompt,
    Prompt_Page,
    OPS_add_main_tab,
    OPS_add_prompt
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
