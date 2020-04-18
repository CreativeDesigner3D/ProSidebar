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

class bp_prompts_OT_add_tab(Operator):
    bl_idname = "bp_prompts.add_tab"
    bl_label = "Add Main Tab"
    bl_options = {'UNDO'}
    
    tab_name: StringProperty(name="Tab Name",default="New Tab")
    # obj: PointerProperty(name="Object",type=bpy.types.Object) #WHY CANNOT I USE POINTER PROPERTY

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


class bp_prompts_OT_add_prompt(Operator):
    bl_idname = "bp_prompts.add_prompt"
    bl_label = "Add Prompt"
    bl_options = {'UNDO'}
    
    obj_name: StringProperty(name="Data Name",default="")

    prompt_name: StringProperty(name="Prompt Name",default="New Prompt")
    prompt_type: EnumProperty(name="Prompt Type",items=prompt_types)
    # the_obj = PointerProperty(name="Object",type=bpy.types.Object) #WHY CANNOT I USE POINTER PROPERTY
    obj = None

    @classmethod
    def poll(cls, context):
        return True

    def get_data(self,context):
        if self.obj_name in bpy.data.objects:
            return bpy.data.objects[self.obj_name]
        else:
            return context.object

    def execute(self, context):
        if self.obj_name in bpy.data.objects:
            self.obj = bpy.data.objects[self.obj_name]        
            self.obj.prompt_page.add_prompt(self.prompt_type,self.prompt_name)
        context.area.tag_redraw()
        return {'FINISHED'}

    def invoke(self,context,event):
        self.obj = context.object
        self.prompt_name = "New Prompt"
        counter = 1
        while self.prompt_name + " " + str(counter) in self.obj.prompt_page.prompts:
            counter += 1
        self.prompt_name = self.prompt_name + " " + str(counter)
            
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Prompt Name")
        row.prop(self,"prompt_name",text="")
        row = layout.row()
        row.label(text="Prompt Type")
        row.prop(self,"prompt_type",text="")


class bp_prompts_OT_add_calculator(Operator):
    bl_idname = "bp_prompts.add_calculator"
    bl_label = "Add Calculator"
    bl_options = {'UNDO'}
    
    obj_name: StringProperty(name="Data Name",default="")

    calculator_name: StringProperty(name="Calculator Name",default="New Prompt")
    # prompt_type: EnumProperty(name="Prompt Type",items=prompt_types)
    # the_obj = PointerProperty(name="Object",type=bpy.types.Object) #WHY CANNOT I USE POINTER PROPERTY
    obj = None

    @classmethod
    def poll(cls, context):
        return True

    def get_data(self,context):
        if self.obj_name in bpy.data.objects:
            return bpy.data.objects[self.obj_name]
        else:
            return context.object

    def execute(self, context):
        if self.obj_name in bpy.data.objects:
            self.obj = bpy.data.objects[self.obj_name]        
            self.obj.prompt_page.add_calculator(self.calculator_name)
        context.area.tag_redraw()
        return {'FINISHED'}

    def invoke(self,context,event):
        self.obj = context.object
        self.calculator_name = "New Calculator"
        counter = 1
        while self.calculator_name + " " + str(counter) in self.obj.prompt_page.calculators:
            counter += 1
        self.calculator_name = self.calculator_name + " " + str(counter)
            
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Calculator Name")
        row.prop(self,"calculator_name",text="")


class bp_prompts_OT_add_calculator_prompt(Operator):
    bl_idname = "bp_prompts.add_calculator_prompt"
    bl_label = "Add Calculator"
    bl_options = {'UNDO'}
    
    calculator_name: StringProperty(name="Calculator Name",default="")
    obj_name: StringProperty(name="Data Name",default="")

    prompt_name: StringProperty(name="Prompt Name",default="New Prompt")
    obj = None

    @classmethod
    def poll(cls, context):
        return True

    def get_data(self,context):
        if self.obj_name in bpy.data.objects:
            return bpy.data.objects[self.obj_name]
        else:
            return context.object

    def get_calculator(self):
        for calculator in self.obj.prompt_page.calculators:
            if calculator.name == self.calculator_name:
                return calculator

    def execute(self, context):
        calculator = self.get_calculator()      
        calculator.add_calculator_prompt(self.prompt_name)
        context.area.tag_redraw()
        return {'FINISHED'}

    def invoke(self,context,event):
        self.obj = context.object
        self.prompt_name = "New Prompt"
        counter = 1
        calculator = self.get_calculator()
        while self.prompt_name + " " + str(counter) in calculator.prompts:
            counter += 1
        self.prompt_name = self.prompt_name + " " + str(counter)
            
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Prompt Name")
        row.prop(self,"prompt_name",text="")


class bp_prompts_OT_edit_calculator(Operator):
    bl_idname = "bp_prompts.edit_calculator"
    bl_label = "Edit Calculator"
    bl_options = {'UNDO'}
    
    calculator_name: StringProperty(name="Calculator Name",default="")
    obj_name: StringProperty(name="Data Name",default="")

    prompt_name: StringProperty(name="Prompt Name",default="New Prompt")
    obj = None
    calculator = None

    @classmethod
    def poll(cls, context):
        return True

    def get_data(self,context):
        if self.obj_name in bpy.data.objects:
            return bpy.data.objects[self.obj_name]
        else:
            return context.object

    def get_calculator(self):
        for calculator in self.obj.prompt_page.calculators:
            if calculator.name == self.calculator_name:
                return calculator

    def execute(self, context):
        context.area.tag_redraw()
        return {'FINISHED'}

    def invoke(self,context,event):
        self.obj = self.get_data(context)
        self.calculator = self.get_calculator()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Calculator Name")
        row.prop(self.calculator,"name",text="")


class bp_prompts_OT_run_calculator(Operator):
    bl_idname = "bp_prompts.run_calculator"
    bl_label = "Run Calculator"
    bl_options = {'UNDO'}
    
    calculator_name: StringProperty(name="Calculator Name",default="")
    obj_name: StringProperty(name="Data Name",default="")

    prompt_name: StringProperty(name="Prompt Name",default="New Prompt")
    obj = None
    calculator = None

    @classmethod
    def poll(cls, context):
        return True

    def get_data(self,context):
        if self.obj_name in bpy.data.objects:
            return bpy.data.objects[self.obj_name]
        else:
            return context.object

    def get_calculator(self):
        for calculator in self.obj.prompt_page.calculators:
            if calculator.name == self.calculator_name:
                return calculator

    def execute(self, context):
        self.obj = self.get_data(context)
        self.calculator = self.get_calculator()
        self.calculator.calculate()
        context.area.tag_redraw()
        return {'FINISHED'}


class bp_prompts_OT_delete_tab(Operator):
    bl_idname = "bp_prompts.delete_tab"
    bl_label = "Delete Tab"
    bl_options = {'UNDO'}

    obj_name: StringProperty(name="Object Name")
    tab_name: StringProperty(name="Tab Name")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.obj_name in bpy.data.objects:
            obj = bpy.data.objects[self.obj_name]
            obj.prompt_page.delete_tab(self.tab_name)
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        layout.label("Are you sure you want to delete the selected tab?")


class bp_prompts_OT_edit_prompt(Operator):
    bl_idname = "bp_prompts.edit_prompt"
    bl_label = "Edit Prompt"
    bl_options = {'UNDO'}
    
    obj_name: StringProperty(name="Object Name",default="") #WHY DON"T POINTERS WORK?
    prompt_name: StringProperty(name="Prompt Name",default="New Prompt")

    prompt = None

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        if self.obj_name in bpy.datga.objects:
            obj = bpy.data.objects[self.obj_name]
            self.prompt = obj.prompt_page.prompts[self.prompt_name]
            wm = context.window_manager
            return wm.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        self.prompt.draw_prompt_properties(layout)


class bp_prompts_OT_add_comboxbox_value(Operator):
    bl_idname = "bp_prompts.add_combobox_value"
    bl_label = "Add Combobox Value"
    bl_options = {'UNDO'}
    
    obj_name: StringProperty(name="Object Name",default="") #WHY DON"T POINTERS WORK?
    prompt_name: StringProperty(name="Prompt Name",default="New Prompt")

    combobox_name: StringProperty(name="Combobox Name",default="Combobox Item")

    prompt = None

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        item = self.prompt.combobox_items.add()
        item.name = self.combobox_name
        context.area.tag_redraw()
        return {'FINISHED'}

    def invoke(self,context,event):
        if self.obj_name in bpy.data.objects:
            obj = bpy.data.objects[self.obj_name]
            self.prompt = obj.prompt_page.prompts[self.prompt_name]
            wm = context.window_manager
            return wm.invoke_props_dialog(self, width=250)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Name")
        row.prop(self,'combobox_name',text="")


class bp_prompts_OT_delete_comboxbox_value(Operator):
    bl_idname = "bp_prompts.delete_combobox_value"
    bl_label = "Delete Combobox Value"
    bl_options = {'UNDO'}
    
    obj_name: StringProperty(name="Object Name",default="") #WHY DON"T POINTERS WORK?
    prompt_name: StringProperty(name="Prompt Name",default="New Prompt")

    combobox_name: StringProperty(name="Combobox Name",default="Combobox Item")

    prompt = None

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        if self.obj_name in bpy.datga.objects:
            obj = bpy.data.objects[self.obj_name]
            self.prompt = obj.prompt_page.prompts[self.prompt_name]
            wm = context.window_manager
            return wm.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Are you sure you want to delete the combobox value")

classes = (
    bp_prompts_OT_add_tab,
    bp_prompts_OT_add_prompt,
    bp_prompts_OT_add_calculator,
    bp_prompts_OT_add_calculator_prompt,
    bp_prompts_OT_edit_calculator,
    bp_prompts_OT_run_calculator,
    bp_prompts_OT_delete_tab,
    bp_prompts_OT_edit_prompt,
    bp_prompts_OT_add_comboxbox_value,
    bp_prompts_OT_delete_comboxbox_value
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
