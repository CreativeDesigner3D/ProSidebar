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

class BP_Window_Manager_Library_Props(bpy.types.PropertyGroup):

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


classes = (
    BP_Window_Manager_Library_Props,
    BP_Scene_Props,
    BP_Collection_Props,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
