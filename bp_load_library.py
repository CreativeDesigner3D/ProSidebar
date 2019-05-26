import bpy
from .bp_utils import utils_library

def register():
    utils_library.update_props_from_xml_file()
    utils_library.load_library_scripts()

def unregister():
    pass 