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
from .ui import bp_view3d_ui_sidebar_render_cycles
from .ui import bp_view3d_ui_sidebar_scene
from .ui import bp_view3d_ui_sidebar_object
from .ui import bp_view3d_ui_sidebar_materials
from .ui import bp_view3d_ui_sidebar_world
from .ui import bp_view3d_ui_sidebar_collections
from .ui import bp_view3d_ui_sidebar_assembly
from .ui import bp_view3d_ui_sidebar_view
from .ops import bp_draw_objects
from .ops import bp_general
from .ops import bp_object
from .ops import bp_material
from .ops import bp_scene
from .ops import bp_world
from .ops import bp_collection
from .ops import bp_assembly
from .ops import bp_driver
from .ops import bp_prompts
from .ops import bp_library
from .ops import bp_library_collection
from .ops import bp_library_material
from .ops import bp_library_object
from . import bp_props
from . import bp_prefs
from . import bp_load_library

def register():
    bp_filebrowser_ui.register()
    bp_view3d_ui_sidebar_render.register()
    bp_view3d_ui_sidebar_render_cycles.register()
    bp_view3d_ui_sidebar_scene.register()
    bp_view3d_ui_sidebar_object.register()
    bp_view3d_ui_sidebar_materials.register()
    bp_view3d_ui_sidebar_world.register()
    bp_view3d_ui_sidebar_collections.register()
    bp_view3d_ui_sidebar_assembly.register()
    bp_view3d_ui_sidebar_view.register()
    bp_draw_objects.register()
    bp_general.register()
    bp_object.register()
    bp_material.register()
    bp_scene.register()
    bp_world.register()
    bp_collection.register()
    bp_assembly.register()
    bp_driver.register()
    bp_prompts.register()
    bp_library.register()
    bp_library_collection.register()
    bp_library_material.register()
    bp_library_object.register()
    bp_props.register()
    bp_prefs.register()
    bp_load_library.register()

def unregister():
    bp_filebrowser_ui.unregister()
    bp_view3d_ui_sidebar_render.unregister()
    bp_view3d_ui_sidebar_render_cycles.unregister()
    bp_view3d_ui_sidebar_scene.unregister()
    bp_view3d_ui_sidebar_object.unregister()
    bp_view3d_ui_sidebar_materials.unregister()
    bp_view3d_ui_sidebar_world.unregister()
    bp_view3d_ui_sidebar_collections.unregister()
    bp_view3d_ui_sidebar_assembly.unregister()
    bp_view3d_ui_sidebar_view.unregister()
    bp_draw_objects.unregister()
    bp_general.unregister()
    bp_object.unregister()
    bp_material.unregister()
    bp_scene.unregister()
    bp_world.unregister()
    bp_collection.unregister()
    bp_assembly.unregister()
    bp_driver.unregister()
    bp_prompts.unregister()
    bp_library.unregister()
    bp_library_collection.unregister()
    bp_library_material.unregister()
    bp_library_object.unregister()    
    bp_props.unregister()
    bp_prefs.unregister()
    bp_load_library.unregister()