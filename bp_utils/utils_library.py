import bpy
import os, sys, inspect
from ..bp_lib.xml import BlenderProXML
import xml.etree.ElementTree as ET
from importlib import import_module

DEFAULT_LIBRARY_ROOT_FOLDER = os.path.join(bpy.utils.user_resource('SCRIPTS'), "creative_designer")
LIBRARY_FOLDER = os.path.join(os.path.dirname(__file__),"data")
LIBRARY_PATH_FILENAME = "creative_designer_paths.xml"

def get_wm_props():
    wm = bpy.context.window_manager
    return wm.bp_lib

def get_thumbnail_file_path():
    return os.path.join(os.path.dirname(__file__),"thumbnail.blend")

def get_library_path_file():
    """ Returns the path to the file that stores all of the library paths.
    """
    # path = os.path.join(bpy.utils.user_resource('SCRIPTS'), "creative_designer")

    if not os.path.exists(DEFAULT_LIBRARY_ROOT_FOLDER):
        os.makedirs(DEFAULT_LIBRARY_ROOT_FOLDER)
        
    return os.path.join(DEFAULT_LIBRARY_ROOT_FOLDER,LIBRARY_PATH_FILENAME)

def get_folder_enum_previews(path,key):
    """ Returns: ImagePreviewCollection
        Par1: path - The path to collect the folders from
        Par2: key - The dictionary key the previews will be stored in
    """
    enum_items = []
    if len(key.my_previews) > 0:
        return key.my_previews
    
    if path and os.path.exists(path):
        folders = []
        for fn in os.listdir(path):
            if os.path.isdir(os.path.join(path,fn)):
                folders.append(fn)

        for i, name in enumerate(folders):
            filepath = os.path.join(path, name)
            thumb = key.load(filepath, "", 'IMAGE')
            filename, ext = os.path.splitext(name)
            enum_items.append((filename, filename, filename, thumb.icon_id, i))
    
    key.my_previews = enum_items
    key.my_previews_dir = path
    return key.my_previews

def get_image_enum_previews(path,key,force_reload=False):
    """ Returns: ImagePreviewCollection
        Par1: path - The path to collect the images from
        Par2: key - The dictionary key the previews will be stored in
    """
    enum_items = []
    if len(key.my_previews) > 0:
        return key.my_previews
    
    if path and os.path.exists(path):
        image_paths = []
        for fn in os.listdir(path):
            if fn.lower().endswith(".png"):
                image_paths.append(fn)

        for i, name in enumerate(image_paths):
            filepath = os.path.join(path, name)
            thumb = key.load(filepath, filepath, 'IMAGE',force_reload)
            filename, ext = os.path.splitext(name)
            enum_items.append((filename, filename, filename, thumb.icon_id, i))
    
    key.my_previews = enum_items
    key.my_previews_dir = path
    return key.my_previews

def create_image_preview_collection():
    import bpy.utils.previews
    col = bpy.utils.previews.new()
    col.my_previews_dir = ""
    col.my_previews = ()
    return col

def write_xml_file():
    '''
    This writes the XML file from the current props. 
    This file gets written everytime a property changes.
    '''
    xml = BlenderProXML()
    root = xml.create_tree()
    paths = xml.add_element(root,'LibraryPaths')
    
    wm = bpy.context.window_manager
    wm_props = wm.bp_lib
    
    if os.path.exists(wm_props.object_library_path):
        xml.add_element_with_text(paths,'Objects',wm_props.object_library_path)
    else:
        xml.add_element_with_text(paths,'Objects',"")
        
    if os.path.exists(wm_props.material_library_path):
        xml.add_element_with_text(paths,'Materials',wm_props.material_library_path)
    else:
        xml.add_element_with_text(paths,'Materials',"")
        
    if os.path.exists(wm_props.collection_library_path):
        xml.add_element_with_text(paths,'Collections',wm_props.collection_library_path)
    else:
        xml.add_element_with_text(paths,'Collections',"")
    
    if os.path.exists(wm_props.script_library_path):
        xml.add_element_with_text(paths,'Scripts',wm_props.script_library_path)
    else:
        xml.add_element_with_text(paths,'Scripts',"")

    xml.write(get_library_path_file())

def update_props_from_xml_file():
    '''
    This gets read on startup and sets the window manager props
    '''
    wm_props = bpy.context.window_manager.bp_lib
    if os.path.exists(get_library_path_file()):
        tree = ET.parse(get_library_path_file())
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
                        
                if item.tag == 'Collections':
                    if os.path.exists(str(item.text)):
                        wm_props.collection_library_path = item.text
                    else:
                        wm_props.collection_library_path = "" 

                if item.tag == 'Scripts':
                    if os.path.exists(str(item.text)):
                        wm_props.script_library_path = item.text
                    else:
                        wm_props.script_library_path = "" 
