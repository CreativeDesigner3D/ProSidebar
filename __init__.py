bl_info = {
    "name": "BlenderPro Sidebar",
    "author": "Andrew Peel",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "Everywhere",
    "description": "New Interfaces for 2.8",
    "warning": "",
    "wiki_url": "",
    "category": "BlenderPro",
}

from .ui import bp_filebrowser_ui
from .ui import bp_view3d_ui_sidebar_render
from .ui import bp_view3d_ui_sidebar_scene
from .ui import bp_view3d_ui_sidebar_object
from .ui import bp_view3d_ui_sidebar_materials
from .ui import bp_view3d_ui_sidebar_world
from .ui import bp_view3d_ui_sidebar_collections
from .ui import bp_view3d_ui_sidebar_assembly
from .ui import bp_view3d_ui_sidebar_view
from .ui import bp_view3d_ui_header
from .ops import bp_library_objects
from .ops import bp_draw_objects
from .ops import bp_general
from .ops import bp_object
from .ops import bp_material
from .ops import bp_scene
from .ops import bp_world
from .ops import bp_collection
from .ops import bp_assembly
from .bp_lib import bp_prompts
from .bp_lib import bp_props
from . import library

def register():
    bp_filebrowser_ui.register()
    bp_view3d_ui_sidebar_render.register()
    bp_view3d_ui_sidebar_scene.register()
    bp_view3d_ui_sidebar_object.register()
    bp_view3d_ui_sidebar_materials.register()
    bp_view3d_ui_sidebar_world.register()
    bp_view3d_ui_sidebar_collections.register()
    bp_view3d_ui_sidebar_assembly.register()
    bp_view3d_ui_sidebar_view.register()
    bp_view3d_ui_header.register()
    bp_draw_objects.register()
    bp_general.register()
    bp_object.register()
    bp_material.register()
    bp_scene.register()
    bp_world.register()
    bp_collection.register()
    bp_assembly.register()
    bp_library_objects.register()
    bp_prompts.register()
    bp_props.register()
    library.register()

def unregister():
    bp_filebrowser_ui.unregister()
    bp_view3d_ui_sidebar_render.unregister()
    bp_view3d_ui_sidebar_scene.unregister()
    bp_view3d_ui_sidebar_object.unregister()
    bp_view3d_ui_sidebar_materials.unregister()
    bp_view3d_ui_sidebar_world.unregister()
    bp_view3d_ui_sidebar_collections.unregister()
    bp_view3d_ui_sidebar_assembly.unregister()
    bp_view3d_ui_sidebar_view.unregister()
    bp_view3d_ui_header.unregister()
    bp_draw_objects.unregister()
    bp_general.unregister()
    bp_object.unregister()
    bp_material.unregister()
    bp_scene.unregister()
    bp_world.unregister()
    bp_collection.unregister()
    bp_assembly.unregister()
    bp_library_objects.unregister()    
    bp_prompts.unregister()
    bp_props.unregister()
    library.unregister()