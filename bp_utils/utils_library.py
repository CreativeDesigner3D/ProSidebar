import bpy
import os, sys, inspect
from ..bp_lib.xml import BlenderProXML
import xml.etree.ElementTree as ET
from importlib import import_module

LIBRARY_FOLDER = os.path.join(os.path.dirname(__file__),"data")
LIBRARY_PATH_FILENAME = "blender_pro_paths.xml"

def get_wm_props():
    wm = bpy.context.window_manager
    return wm.bp_lib

def get_thumbnail_file_path():
    return os.path.join(os.path.dirname(__file__),"thumbnail.blend")

def get_library_path_file():
    """ Returns the path to the file that stores all of the library paths.
    """
    path = os.path.join(bpy.utils.user_resource('SCRIPTS'), "blender_pro")

    if not os.path.exists(path):
        os.makedirs(path)
        
    return os.path.join(path,LIBRARY_PATH_FILENAME)

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

def load_library_scripts():
    wm_props = bpy.context.window_manager.bp_lib

    # Store all library paths
    library_paths = []

    # Search for internal library paths
    internal_library_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'library','scripts')
    folders = os.listdir(internal_library_path)
    for folder in folders:
        lib_path = os.path.join(internal_library_path,folder)
        if os.path.isdir(lib_path):
            library_paths.append(lib_path)

    #This is being run multiple times on debug startup so remove all items first
    for item in wm_props.library_items:
        wm_props.library_items.remove(0)

    #Load all Libraries
    for path in library_paths:
        print('Loading Library: ',path)
        if os.path.exists(path):
            files = os.listdir(path)
            for file in files:
                if file == '__init__.py':
                    path, folder_name = os.path.split(os.path.normpath(path))
                    sys.path.append(path)
                    pkg = import_module(folder_name)
                    for mod_name, mod in inspect.getmembers(pkg):
                        if mod_name[:2] != "__": #No need to go through built in modules
                            for name, obj in inspect.getmembers(mod):
                                if hasattr(obj,'show_in_library') and obj.show_in_library:
                                    
                                    item = wm_props.library_items.add()
                                    item.package_name = folder_name
                                    item.module_name = mod_name
                                    item.class_name = name
                                    item.name = name

