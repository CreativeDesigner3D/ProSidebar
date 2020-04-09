import bpy
import inspect
from .bp_utils import utils_library
from . import bp_driver_functions
from bpy.app.handlers import persistent

@persistent
def load_driver_functions(scene):
    """ Load Default Drivers
    """
    for name, obj in inspect.getmembers(bp_driver_functions):
        if name not in bpy.app.driver_namespace:
            bpy.app.driver_namespace[name] = obj

@persistent
def load_library_on_file_load(scene=None):
    utils_library.update_props_from_xml_file()

def register():
    bpy.app.handlers.load_post.append(load_library_on_file_load)
    bpy.app.handlers.load_post.append(load_driver_functions)

def unregister():
    bpy.app.handlers.load_post.remove(load_library_on_file_load)  
    bpy.app.handlers.load_post.remove(load_driver_functions)  