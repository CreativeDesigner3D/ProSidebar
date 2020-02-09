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
import os
from .bp_utils import utils_library

prompt_types = [('FLOAT',"Float","Float"),
                ('DISTANCE',"Distance","Distance"),
                ('ANGLE',"Angle","Angle"),
                ('QUANTITY',"Quantity","Quantity"),
                ('PERCENTAGE',"Percentage","Percentage"),
                ('CHECKBOX',"Checkbox","Checkbox"),
                ('COMBOBOX',"Combobox","Combobox"),
                ('TEXT',"Text","Text")]

def add_driver_variables(driver,variables):
    for var in variables:
        new_var = driver.driver.variables.new()
        new_var.type = 'SINGLE_PROP'
        new_var.name = var.name
        new_var.targets[0].data_path = var.data_path
        new_var.targets[0].id = var.obj

def update_object_selection(self,context):
    if self.selected_object_index < len(context.scene.objects):
        bpy.ops.object.select_all(action = 'DESELECT')
        obj = context.scene.objects[self.selected_object_index]
        obj.select_set(True)
        context.view_layer.objects.active = obj

def update_object_selection_from_collection(self,context):
    if self.selected_object_index < len(context.view_layer.active_layer_collection.collection.objects):
        bpy.ops.object.select_all(action = 'DESELECT')
        obj = context.view_layer.active_layer_collection.collection.objects[self.selected_object_index]
        obj.select_set(True)
        context.view_layer.objects.active = obj

def update_world_selection(self,context):
    if self.selected_world_index <= len(bpy.data.worlds) - 1:
        world = bpy.data.worlds[self.selected_world_index]
        context.scene.world = world

def update_library_paths(self,context):
    utils_library.write_xml_file()

def update_library_tab(self,context):
    root_path = utils_library.get_active_library_path(self.library_tabs)
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    folders = utils_library.get_active_categories(self.library_tabs)
    active_folder_name = utils_library.get_active_category(self,folders)
    utils_library.update_file_browser_path(context,os.path.join(root_path,active_folder_name))

class Variable():

    obj = None
    data_path = ""
    name = ""

    def __init__(self,obj,data_path,name):
        self.obj = obj
        self.data_path = data_path
        self.name = name


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
    combobox_columns: IntProperty(name="Combobox Columns",default=1,min=1)

    def get_var(self,name):
        prompt_path = 'prompt_page.prompts["' + self.name + '"]'
        if self.prompt_type == 'FLOAT':
            return Variable(self.id_data, prompt_path + '.float_value',name)
        if self.prompt_type == 'DISTANCE':
            return Variable(self.id_data, prompt_path + '.distance_value',name)
        if self.prompt_type == 'ANGLE':
            return Variable(self.id_data, prompt_path + '.angle_value',name)
        if self.prompt_type == 'QUANTITY':
            return Variable(self.id_data, prompt_path + '.quantity_value',name)
        if self.prompt_type == 'PERCENTAGE':
            return Variable(self.id_data, prompt_path + '.percentage_value',name)
        if self.prompt_type == 'CHECKBOX':
            return Variable(self.id_data, prompt_path + '.checkbox_value',name)
        if self.prompt_type == 'COMBOBOX':
            return Variable(self.id_data, prompt_path + '.combobox_index',name) #TODO: IMPLEMENT UI LIST
        if self.prompt_type == 'TEXT':
            return Variable(self.id_data, prompt_path + '.text_value',name)       

    def set_value(self,value):
        if self.prompt_type == 'FLOAT':
            self.float_value = value
        if self.prompt_type == 'DISTANCE':
            self.distance_value = value
        if self.prompt_type == 'ANGLE':
            self.angle_value = value
        if self.prompt_type == 'QUANTITY':
            self.quantity_value = value
        if self.prompt_type == 'PERCENTAGE':
            self.percentage_value = value
        if self.prompt_type == 'CHECKBOX':
            self.checkbox_value = value
        if self.prompt_type == 'COMBOBOX':
            self.combobox_index = value #TODO: IMPLEMENT UI LIST
        if self.prompt_type == 'TEXT':
            self.text_value = value

    def set_formula(self,expression,variables):
        prompt_path = 'prompt_page.prompts["' + self.name + '"]'
        data_path = ""
        if self.prompt_type == 'FLOAT':
            data_path = prompt_path + '.float_value'
        if self.prompt_type == 'DISTANCE':
            data_path = prompt_path + '.distance_value'
        if self.prompt_type == 'ANGLE':
            data_path = prompt_path + '.angle_value'
        if self.prompt_type == 'QUANTITY':
            data_path = prompt_path + '.quantity_value'
        if self.prompt_type == 'PERCENTAGE':
            data_path = prompt_path + '.precentage_value'
        if self.prompt_type == 'CHECKBOX':
            data_path = prompt_path + '.checkbox_value'
        if self.prompt_type == 'COMBOBOX':
            data_path = prompt_path + '.combobox_index'
        if self.prompt_type == 'TEXT':
            data_path = prompt_path + '.text_value'

        driver = self.id_data.driver_add(data_path)
        add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def draw_prompt_properties(self,layout):
        pass #RENAME PROMPT, #LOCK VALUE, #TAB INDEX, #IF COMBOBOX THEN COLUMN NUMBER

    def draw(self,layout):
        row = layout.row()
        row.label(text=self.name)
        if self.prompt_type == 'FLOAT':
            row.prop(self,"float_value",text="")
        if self.prompt_type == 'DISTANCE':
            row.prop(self,"distance_value",text="")
        if self.prompt_type == 'ANGLE':
            row.prop(self,"angle_value",text="")
        if self.prompt_type == 'QUANTITY':
            row.prop(self,"quantity_value",text="")
        if self.prompt_type == 'PERCENTAGE':
            row.prop(self,"percentage_value",text="")
        if self.prompt_type == 'CHECKBOX':
            row.prop(self,"checkbox_value",text="")
        if self.prompt_type == 'COMBOBOX':
            props = row.operator('bp_prompts.add_combobox_value',text="",icon='ADD')
            props.obj_name = self.id_data.name
            props.prompt_name = self.name
            row.operator('bp_prompts.delete_combobox_value',text="",icon='X')
            props.obj_name = self.id_data.name
            props.prompt_name = self.name            
            col = layout.column()
            col.template_list("FD_UL_combobox"," ", self, "combobox_items", self, "combobox_index",
                              rows=len(self.combobox_items)/self.combobox_columns,type='GRID',columns=self.combobox_columns)

        if self.prompt_type == 'TEXT':
            row.prop(self,"text_value",text="")


class Calculator_Prompt(PropertyGroup):
    distance_value: FloatProperty(name="Distance Value",subtype='DISTANCE')
    equal: BoolProperty(name="Equal",default=True)

    def draw(self,layout):
        pass


class Calculator(PropertyGroup):
    prompts: CollectionProperty(name="Prompts",type=Calculator_Prompt)
    total_distance: FloatProperty(name="Distance Value",subtype='DISTANCE')

    def set_total_distance(self,expression="",variables=[],value=0):
        pass

    def draw_calculator(self,layout):
        pass

    def add_calculator_prompt(self,name):
        prompt = self.prompts.add()
        prompt.name = name

    def remove_calculator_prompt(self,name):
        pass

    def calculate(self):
        non_equal_prompts_total_value = 0
        equal_prompt_qty = 0
        calc_prompts = []
        for prompt in self.prompts:
            if prompt.equal:
                equal_prompt_qty += 1
                calc_prompts.append(prompt)
            else:
                non_equal_prompts_total_value += prompt.distance_value

        if equal_prompt_qty > 0:
            prompt_value = (self.total_distance - non_equal_prompts_total_value) / equal_prompt_qty

            for prompt in calc_prompts:
                prompt.distance_value = prompt_value

            self.id_data.location = self.id_data.location #NOT SURE THIS IS NEEDED


class Prompt_Page(PropertyGroup):
    tabs: CollectionProperty(type=Tab, name="Tabs")
    tab_index: IntProperty(name="Tab Index")
    prompts: CollectionProperty(type=Prompt, name="Prompts")
    calculators: CollectionProperty(type=Calculator, name="Calculators")
    
    @classmethod
    def register(cls):
        bpy.types.Object.prompt_page = PointerProperty(
            name="Prompt Page",
            description="Blender Pro Prompts",
            type=cls,
        )

    @classmethod
    def unregister(cls):
        del bpy.types.Object.prompt_page

    def add_tab(self,name):
        tab = self.tabs.add()
        tab.name = name

    def delete_prompt(self,name):
        for index, prompt in enumerate(self.prompts):
            if prompt.name == name:
                self.prompts.remove(index)

    def delete_tab(self,name):
        for index, tab in enumerate(self.tab):
            if tab.name == name:
                self.tabs.remove(index)

    def draw_prompts(self,layout):
        props = layout.operator('bp_prompts.add_prompt')
        props.obj_name = self.id_data.name
        for prompt in self.prompts:
            prompt.draw(layout)
    
    def add_prompt(self,prompt_type,prompt_name):
        prompt = self.prompts.add()
        prompt.prompt_type = prompt_type
        prompt.name = prompt_name
        prompt.tab_index = self.tab_index
        return prompt


class Script_Library_Item(bpy.types.PropertyGroup):
    package_name: bpy.props.StringProperty(name="Package Name")
    module_name: bpy.props.StringProperty(name="Module Name")
    class_name: bpy.props.StringProperty(name="Class Name")
    placement_id: bpy.props.StringProperty(name="Placement ID")
    prompts_id: bpy.props.StringProperty(name="Prompts ID")
    render_id: bpy.props.StringProperty(name="Render ID")
    category_name: bpy.props.StringProperty(name="Category Name")
    # tags: bpy.props.CollectionProperty(name="Tags", type=Tag) #TODO: Implement Tags


class Script_Library(bpy.types.PropertyGroup):
    library_items: bpy.props.CollectionProperty(name="Library Items", type=Script_Library_Item)
    library_path: bpy.props.StringProperty(name="Library Path")
    panel_id: bpy.props.StringProperty(name="Panel ID")


class AP_Object_Driver_Props(PropertyGroup):
    show_driver_debug_info: BoolProperty(name="Show Driver Debug Info", default=False)
    
    def get_var(self,data_path,name):
        return Variable(self.id_data,data_path,name)

    def modifier(self,modifier,property_name,index=-1,expression="",variables=[]):
        driver = modifier.driver_add(property_name,index)
        add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def loc_x(self,expression,variables):
        driver = self.id_data.driver_add('location',0)
        add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def loc_y(self,expression,variables):
        driver = self.id_data.driver_add('location',1)
        add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def loc_z(self,expression,variables):
        driver = self.id_data.driver_add('location',2)
        add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def rot_x(self,expression,variables):
        driver = self.id_data.driver_add('rotation_euler',0)
        add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def rot_y(self,expression,variables):
        driver = self.id_data.driver_add('rotation_euler',1)
        add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def rot_z(self,expression,variables):
        driver = self.id_data.driver_add('rotation_euler',2)
        add_driver_variables(driver,variables)
        driver.driver.expression = expression

    @classmethod
    def register(cls):
        bpy.types.Object.drivers = PointerProperty(name="Drivers Props",description="Driver Props",type=cls)
        
    @classmethod
    def unregister(cls):
        del bpy.types.Object.drivers


class BP_Window_Manager_Library_Props(bpy.types.PropertyGroup):

    file_browser_search_text: bpy.props.StringProperty(name="File Browser Search Text")
    script_libraries: CollectionProperty(name="Script_Libraries",type=Script_Library)

    object_library_path: bpy.props.StringProperty(name="Object Library Path",
                                                   default="",
                                                   subtype='DIR_PATH',
                                                   update=update_library_paths)
    
    collection_library_path: bpy.props.StringProperty(name="Collection Library Path",
                                                  default="",
                                                  subtype='DIR_PATH',
                                                  update=update_library_paths)
    
    material_library_path: bpy.props.StringProperty(name="Material Library Path",
                                                     default="",
                                                     subtype='DIR_PATH',
                                                     update=update_library_paths)        

    world_library_path: bpy.props.StringProperty(name="World Library Path",
                                                     default="",
                                                     subtype='DIR_PATH',
                                                     update=update_library_paths)   

    script_library_path: bpy.props.StringProperty(name="Script Library Path",
                                                  default="",
                                                  subtype='DIR_PATH',
                                                  update=update_library_paths)

    object_category: bpy.props.StringProperty(name="Object Category",
                                               default="",
                                               update=update_library_paths)   
        
    collection_category: bpy.props.StringProperty(name="Collection Category",
                                              default="",
                                              update=update_library_paths)  
    
    material_category: bpy.props.StringProperty(name="Material Category",
                                                 default="",
                                                 update=update_library_paths)  
                
    world_category: bpy.props.StringProperty(name="World Category",
                                                 default="",
                                                 update=update_library_paths)                  

    @classmethod
    def register(cls):
        bpy.types.WindowManager.bp_lib = bpy.props.PointerProperty(
            name="BP Library",
            description="Library Properties",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.bp_lib


class BP_Scene_Props(PropertyGroup):
    library_tabs: bpy.props.EnumProperty(name="Library Tabs",
                                         items=[('OBJECT',"Object","Show the Object Library"),
                                                ('COLLECTION',"Collection","Show the Collection Library"),
                                                ('MATERIAL',"Material","Show the Material Library"),
                                                ('WORLD',"World","Show the World Library"),
                                                ('SCRIPT',"Script","Show the Script Library")],
                                         default='SCRIPT',
                                         update=update_library_tab)

    active_script_library: StringProperty(name="Active Script Library",default="")
    active_script_category: StringProperty(name="Active Script Category",default="")
    active_object_library: StringProperty(name="Active Object Library",default="")
    active_collection_library: StringProperty(name="Active Collection Library",default="")
    active_material_library: StringProperty(name="Active Material Library",default="")
    active_world_library: StringProperty(name="Active World Library",default="")

    selected_object_index: IntProperty(name="Selected Object Index", default=0, update = update_object_selection)
    selected_world_index: IntProperty(name="Selected World Index", default=0, update = update_world_selection)
    selected_material_index: IntProperty(name="Selected Material Index", default=0)

    @classmethod
    def register(cls):
        bpy.types.Scene.bp_props = PointerProperty(
            name="BP Props",
            description="ProSidebar Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.bp_props


class BP_Collection_Props(PropertyGroup):
    is_expanded: BoolProperty(name="Is Expanded", default=False)
    selected_object_index: IntProperty(name="Select Object Index", default=False,update = update_object_selection_from_collection)

    @classmethod
    def register(cls):
        bpy.types.Collection.bp_props = PointerProperty(name="BP Props",description="Blender Pro Props",type=cls)
        
    @classmethod
    def unregister(cls):
        del bpy.types.Collection.bp_props

#MAYBE THIS SHOULDN'T BE HERE
class FD_UL_combobox(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name)


classes = (
    Combobox_Item,
    Tab,
    Prompt,
    Calculator_Prompt,
    Calculator,
    Prompt_Page,
    Script_Library_Item,
    Script_Library,    
    AP_Object_Driver_Props,
    BP_Window_Manager_Library_Props,
    BP_Scene_Props,
    BP_Collection_Props,
    FD_UL_combobox
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
