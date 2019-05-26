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

from .bp_utils import utils_library

prompt_types = [('FLOAT',"Float","Float"),
                ('DISTANCE',"Distance","Distance"),
                ('ANGLE',"Angle","Angle"),
                ('QUANTITY',"Quantity","Quantity"),
                ('PERCENTAGE',"Percentage","Percentage"),
                ('CHECKBOX',"Checkbox","Checkbox"),
                ('COMBOBOX',"Combobox","Combobox"),
                ('TEXT',"Text","Text")]


def update_scene_selection(self,context):
    pass
    #TODO: Figure out how to change scene
    # context.scene = bpy.data.scenes[self.selected_scene_index] 
    # if context.screen.scene.outliner.selected_scene_index != self.selected_scene_index:
    #     context.screen.scene.outliner.selected_scene_index = self.selected_scene_index

def update_object_selection(self,context):
    if self.selected_object_index < len(context.scene.objects):
        bpy.ops.object.select_all(action = 'DESELECT')
        obj = context.scene.objects[self.selected_object_index]
        obj.select_set(True)
        context.view_layer.objects.active = obj

def update_world_selection(self,context):
    if self.selected_world_index <= len(bpy.data.worlds) - 1:
        world = bpy.data.worlds[self.selected_world_index]
        context.scene.world = world


class Variable():

    obj = None
    data_path = ""
    name = ""

    def __init__(self,obj,data_path,name):
        self.obj = obj
        self.data_path = data_path
        self.name = name


def add_driver_variables(driver,variables):
    for var in variables:
        new_var = driver.driver.variables.new()
        new_var.type = 'SINGLE_PROP'
        new_var.name = var.name
        new_var.targets[0].data_path = var.data_path
        new_var.targets[0].id = var.obj

def update_library_paths(self,context):
    utils_library.write_xml_file()


class Tag(bpy.types.PropertyGroup):
    pass


class Library_Item(bpy.types.PropertyGroup):
    package_name: bpy.props.StringProperty(name="Package Name")
    module_name: bpy.props.StringProperty(name="Module Name")
    class_name: bpy.props.StringProperty(name="Class Name")
    placement_id: bpy.props.StringProperty(name="Placement ID")
    prompts_id: bpy.props.StringProperty(name="Prompts ID")
    tags: bpy.props.CollectionProperty(name="Tags", type=Tag)


class BP_Window_Manager_Library_Props(bpy.types.PropertyGroup):
    library_items: bpy.props.CollectionProperty(name="Library Items", type=Library_Item)

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
                

    @classmethod
    def register(cls):
        bpy.types.WindowManager.bp_lib = bpy.props.PointerProperty(
            name="BP Library",
            description="Blender Pro Library Properties",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.bp_lib


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

    def get_var(self,name):
        if self.prompt_type == 'FLOAT':
            return Variable(self.id_data,'prompt_page.prompts["' + self.name + '"].float_value',name)
        if self.prompt_type == 'DISTANCE':
            return Variable(self.id_data,'prompt_page.prompts["' + self.name + '"].distance_value',name)
        if self.prompt_type == 'ANGLE':
            return Variable(self.id_data,'prompt_page.prompts["' + self.name + '"].angle_value',name)
        if self.prompt_type == 'QUANTITY':
            return Variable(self.id_data,'prompt_page.prompts["' + self.name + '"].quantity_value',name)
        if self.prompt_type == 'PERCENTAGE':
            return Variable(self.id_data,'prompt_page.prompts["' + self.name + '"].percentage_value',name)
        if self.prompt_type == 'CHECKBOX':
            return Variable(self.id_data,'prompt_page.prompts["' + self.name + '"].checkbox_value',name)
        if self.prompt_type == 'COMBOBOX':
            return Variable(self.id_data,'prompt_page.prompts["' + self.name + '"].combobox_index',name) #TODO: IMPLEMENT UI LIST
        if self.prompt_type == 'TEXT':
            return Variable(self.id_data,'prompt_page.prompts["' + self.name + '"].text_value',name)       

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
        driver = self.id_data.driver_add('prompt_page.prompts["' + self.name + '"].distance_value')
        add_driver_variables(driver,variables)
        driver.driver.expression = expression

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
            row.prop(self,"combobox_index",text="") #TODO: IMPLEMENT UI LIST
        if self.prompt_type == 'TEXT':
            row.prop(self,"text_value",text="")


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

    @classmethod
    def unregister(cls):
        del bpy.types.Object.prompt_page

    def add_tab(self,name):
        tab = self.tabs.add()
        tab.name = name

    def draw_prompts(self,layout,data_type):
        props = layout.operator('bp_prompts.add_prompt')
        props.data_type = data_type
        props.data_name = self.id_data.name
        for prompt in self.prompts:
            prompt.draw(layout)
    
    def add_prompt(self,prompt_type,prompt_name):
        prompt = self.prompts.add()
        prompt.prompt_type = prompt_type
        prompt.name = prompt_name
        prompt.tab_index = self.tab_index
        return prompt


class BP_Scene_Props(PropertyGroup):
    selected_scene_index: IntProperty(name="Selected Scene Index", default=0, update = update_scene_selection)
    selected_object_index: IntProperty(name="Selected Object Index", default=0, update = update_object_selection)
    selected_world_index: IntProperty(name="Selected World Index", default=0, update = update_world_selection)
    selected_material_index: IntProperty(name="Selected Material Index", default=0)
    
    object_tabs: bpy.props.EnumProperty(name="Object Tabs",
                                        items=[('MAIN',"Main","Show the Scene Options"),
                                               ('MATERIAL',"Material","Show the Material Options"),
                                               ('MODIFIERS',"Modifiers","Show the Modifiers"),
                                               ('LOGIC',"Logic","Show the Drivers")],
                                        default='MAIN')
    
    @classmethod
    def register(cls):
        bpy.types.Scene.bp_props = PointerProperty(
            name="BP Props",
            description="Blender Pro Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.bp_props


class BP_Collection_Props(PropertyGroup):
    is_expanded: BoolProperty(name="Is Expanded", default=False)
    selected_object_index: IntProperty(name="Select Object Index", default=False)
    assembly_tabs: bpy.props.EnumProperty(name="Assembly Tabs",
                                          items=[('MAIN',"Main","Show the Scene Options"),
                                                 ('PROMPTS',"Prompts","Show the Assembly Prompts"),
                                                 ('OBJECTS',"Objects","Show the Objects"),
                                                 ('LOGIC',"Logic","Show the Driver Logic")],
                                          default='MAIN')
    @classmethod
    def register(cls):
        bpy.types.Collection.bp_props = PointerProperty(name="BP Props",description="Blender Pro Props",type=cls)
        
    @classmethod
    def unregister(cls):
        del bpy.types.Collection.bp_props


class BP_Object_Props(PropertyGroup):
    show_driver_debug_info: BoolProperty(name="Show Driver Debug Info", default=False)

    def hook_vertex_group_to_object(self,vertex_group,obj_hook):
        """ This function adds a hook modifier to the verties 
            in the vertex_group to the obj_hook
        """
        bpy.ops.object.select_all(action = 'DESELECT')
        obj_hook.hide_set(False)
        obj_hook.hide_select = False
        obj_hook.select_set(True)
        self.id_data.hide_set(False)
        self.id_data.hide_select = False
        if vertex_group in self.id_data.vertex_groups:
            vgroup = self.id_data.vertex_groups[vertex_group]
            self.id_data.vertex_groups.active_index = vgroup.index
            bpy.context.view_layer.objects.active = self.id_data
            bpy.ops.bp_object.toggle_edit_mode(obj_name=self.id_data.name)
            bpy.ops.mesh.select_all(action = 'DESELECT')
            bpy.ops.object.vertex_group_select()
            if self.id_data.data.total_vert_sel > 0:
                bpy.ops.object.hook_add_selob()
            bpy.ops.mesh.select_all(action = 'DESELECT')
            bpy.ops.bp_object.toggle_edit_mode(obj_name=self.id_data.name)

    @classmethod
    def register(cls):
        bpy.types.Object.bp_props = PointerProperty(name="BP Props",description="Blender Pro Props",type=cls)
        
    @classmethod
    def unregister(cls):
        del bpy.types.Object.bp_props


class BP_Object_Driver_Props(PropertyGroup):
    
    def get_var(self,data_path,name):
        return Variable(self.id_data,data_path,name)

    def x_loc(self,expression,variables):
        driver = self.id_data.driver_add('location',0)
        add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def y_loc(self,expression,variables):
        driver = self.id_data.driver_add('location',1)
        add_driver_variables(driver,variables)
        driver.driver.expression = expression

    def z_loc(self,expression,variables):
        driver = self.id_data.driver_add('location',2)
        add_driver_variables(driver,variables)
        driver.driver.expression = expression

    @classmethod
    def register(cls):
        bpy.types.Object.drivers = PointerProperty(name="BP Props",description="Blender Pro Props",type=cls)
        
    @classmethod
    def unregister(cls):
        del bpy.types.Object.drivers

classes = (
    Tag,
    Library_Item,
    BP_Window_Manager_Library_Props,
    Combobox_Item,
    Tab,
    Prompt,
    Prompt_Page,    
    BP_Scene_Props,
    BP_Collection_Props,
    BP_Object_Props,
    BP_Object_Driver_Props,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
