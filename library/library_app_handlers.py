import bpy
import os
from . import utils_library
import xml.etree.ElementTree as ET
from bpy.app.handlers import persistent

@persistent
def update_library_paths_on_startup(scene=None):
    wm_props = bpy.context.window_manager.bp_lib
    if os.path.exists(utils_library.get_library_path_file()):
        tree = ET.parse(utils_library.get_library_path_file())
        root = tree.getroot()
        for elm in root.findall("LibraryPaths"):
            items = elm.getchildren()
            for item in items:
                
                if item.tag == 'Objects':
                    if os.path.exists(str(item.text)):
                        wm_props.object_library_path = item.text
                    else:
                        wm_props.object_library_path = ""
                        
                if item.tag == 'Materials':
                    if os.path.exists(str(item.text)):
                        wm_props.material_library_path = item.text
                    else:
                        wm_props.material_library_path = ""
                        
                if item.tag == 'Groups':
                    if os.path.exists(str(item.text)):
                        wm_props.group_library_path = item.text
                    else:
                        wm_props.group_library_path = "" 


def register():
    update_library_paths_on_startup(None)
    bpy.app.handlers.load_post.append(update_library_paths_on_startup) #NOT SURE IF THIS IS NEEDED ANYMORE

def unregister():
    pass #TODO: Figure out how to unregister app handlers