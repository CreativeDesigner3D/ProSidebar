import bpy
import os
from . import utils_library
from ..bp_lib.xml import BlenderProXML

def update_library_paths(self,context):
    utils_library.write_xml_file()

class PROPS_window_manager(bpy.types.PropertyGroup):
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

classes = (
    PROPS_window_manager,
)

register, unregister = bpy.utils.register_classes_factory(classes)