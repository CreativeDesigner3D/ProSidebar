'''
Created on Oct 9, 2018

@author: Andrew
'''
bl_info = {
    "name": "BlenderPro File Browser",
    "author": "Andrew Peel",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "Filebrowser",
    "description": "New File Browser Interface for 2.8",
    "warning": "",
    "wiki_url": "",
    "category": "BlenderPro",
}


import bpy
import os
from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        Header,
        )
from bpy.props import (
        BoolProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        )

class FILEBROWSER_PT_quick_navigation(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_label = "Quick Navigation"
    bl_ui_units_x = 13

    def draw(self, context):
        layout = self.layout
        layout.label(text="Quick Navigation")
        layout.menu('FILEBROWSER_MT_recent_folders') 
        layout.menu('FILEBROWSER_MT_bookmark_folders') 

class FILEBROWSER_PT_view_options(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_label = "View Options"
    bl_ui_units_x = 13

    def draw(self, context):
        layout = self.layout
        layout.label(text="View Options")
        layout.operator_context = 'EXEC_DEFAULT'
        layout.operator("file.directory_new", icon='NEWFOLDER', text="Create New Folder")
        
        st = context.space_data
        params = st.params
        is_lib_browser = params.use_library_browsing
        
        col = layout.column(align=True)
        col.label(text="Display Type:")
        col.prop(params, "display_type", expand=True, text="Display Type")
        
        col = layout.column(align=True)
        col.label(text="Sort Type:")
        col.prop(params, "sort_method", expand=True, text="Sort Files")
        
        layout.prop(params, "show_hidden", text="Show Hidden Files")        
        
        if params.filter_glob:
            # if st.active_operator and hasattr(st.active_operator, "filter_glob"):
            #     row.prop(params, "filter_glob", text="")
            layout.label(text=params.filter_glob)
        else:
            col = layout.column(align=True)
            col.label(text="Filter Options:",icon='FILTER')
            col.prop(params, "use_filter_blender", text="Blender Files")
            col.prop(params, "use_filter_backup", text="Blender Backup Files")
            col.prop(params, "use_filter_image", text="Image Files")
            col.prop(params, "use_filter_movie", text="Move Files")
            col.prop(params, "use_filter_script", text="Python Files")
            col.prop(params, "use_filter_font", text="Font Files")
            col.prop(params, "use_filter_sound", text="Sound Files")
            col.prop(params, "use_filter_text", text="Text Files")
        
        if is_lib_browser:
            layout.prop(params, "use_filter_blendid", text="")
            if params.use_filter_blendid:
                layout.separator()
                layout.prop(params, "filter_id_category", text="")
                
        

class FILEBROWSER_HT_header(bpy.types.Header):
    bl_space_type = 'FILE_BROWSER'

    def splitall(self,path):
        allparts = []
        while 1:
            parts = os.path.split(path)
            if parts[0] == path:  # sentinel for absolute paths
                allparts.insert(0, parts[0])
                break
            elif parts[1] == path: # sentinel for relative paths
                allparts.insert(0, parts[1])
                break
            else:
                path = parts[0]
                allparts.insert(0, parts[1])
        return allparts

    def draw(self, context):
        layout = self.layout

        st = context.space_data
        params = st.params

        if st.active_operator is None:
            layout.template_header()

        layout.popover(panel="FILEBROWSER_PT_view_options")
        layout.menu('FILEBROWSER_MT_recent_folders',text="Recent") 
#         layout.popover(panel="FILEBROWSER_PT_quick_navigation")
        
        
#         layout.menu("FILEBROWSER_MT_view")

        row = layout.row(align=True)
        row.operator("file.previous", text="", icon='BACK')
        row.operator("file.next", text="", icon='FORWARD')
        row.operator("file.parent", text="", icon='FILE_PARENT')
        row.operator("file.refresh", text="", icon='FILE_REFRESH')

        folders = self.splitall(params.directory)
        current_path = ""
        row = layout.row(align=True)
        for folder in folders:
            current_path = os.path.join(current_path,folder)
            if folder != "":
                row.operator("filebrowser.go_to_dir",text=folder).path = current_path
            
        layout.operator_context = 'INVOKE_DEFAULT'

        layout.separator_spacer()
        layout.prop(params, "filter_search", text="Search", icon='VIEWZOOM')
        
        # can be None when save/reload with a file selector open
#         if params:
#             is_lib_browser = params.use_library_browsing
# 
#             layout.prop(params, "display_type", expand=True, text="")
#             layout.prop(params, "sort_method", expand=True, text="")
#             layout.prop(params, "show_hidden", text="", icon='FILE_HIDDEN')
# 
#         layout.separator_spacer()
# 
#         layout.template_running_jobs()

#         if params:
#             layout.prop(params, "use_filter", text="", icon='FILTER')
# 
#             row = layout.row(align=True)
#             row.active = params.use_filter
#             row.prop(params, "use_filter_folder", text="")
# 
#             if params.filter_glob:
#                 # if st.active_operator and hasattr(st.active_operator, "filter_glob"):
#                 #     row.prop(params, "filter_glob", text="")
#                 row.label(text=params.filter_glob)
#             else:
#                 row.prop(params, "use_filter_blender", text="")
#                 row.prop(params, "use_filter_backup", text="")
#                 row.prop(params, "use_filter_image", text="")
#                 row.prop(params, "use_filter_movie", text="")
#                 row.prop(params, "use_filter_script", text="")
#                 row.prop(params, "use_filter_font", text="")
#                 row.prop(params, "use_filter_sound", text="")
#                 row.prop(params, "use_filter_text", text="")
# 
#             if is_lib_browser:
#                 row.prop(params, "use_filter_blendid", text="")
#                 if params.use_filter_blendid:
#                     row.separator()
#                     row.prop(params, "filter_id_category", text="")
# 
#             row.separator()
#             row.prop(params, "filter_search", text="", icon='VIEWZOOM')


class FILEBROWSER_MT_recent_folders(bpy.types.Menu):
    bl_label = "Recent Folders"
    
    def draw(self, context):
        layout = self.layout
        space = context.space_data
        for recent in space.recent_folders:
            layout.operator('filebrowser.go_to_dir',text=recent.path).path = recent.path

class FILEBROWSER_MT_bookmark_folders(bpy.types.Menu):
    bl_label = "Bookmark Folders"
    
    def draw(self, context):
        layout = self.layout
        space = context.space_data
        for recent in space.recent_folders:
            layout.operator('filebrowser.go_to_dir',text=recent.path).path = recent.path
        layout.separator()
        layout.operator('filebrowser.go_to_dir',text="Add New Bookmark")

class FILEBROWSER_OT_go_to_dir(Operator):
    bl_idname = "filebrowser.go_to_dir"
    bl_label = "Go To Dir"
    bl_description = "Go to Dir"
    bl_options = {'REGISTER', 'UNDO'}
    
    path: StringProperty(name="Path")

    def execute(self, context):
        params = context.space_data.params
        params.directory = self.path
        return {'FINISHED'}

def clear_file_browser_header():
    if hasattr(bpy.types, 'FILEBROWSER_HT_header'):
        bpy.utils.unregister_class(bpy.types.FILEBROWSER_HT_header)
        
clear_file_browser_header()            
            

class USERPREF_HT_header(Header):
    bl_space_type = 'PREFERENCES'

    def draw(self, _context):            
        pass
            
class USERPREF_PT_navigation(Panel):
    bl_label = "Preferences Navigation"
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'NAVIGATION_BAR'
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        pass

class USERPREF_PT_save_preferences(Panel):
    bl_label = "Save Preferences"
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'EXECUTE'
    bl_options = {'HIDE_HEADER'}

    def draw(self, _context):
        pass

class PreferencePanel(Panel):
    """
    Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a ``draw_props(context, layout)`` function.
    """

    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'

    def draw(self, context):
        pass

classes = (
    FILEBROWSER_HT_header,
    FILEBROWSER_PT_view_options,
    FILEBROWSER_OT_go_to_dir,
    FILEBROWSER_MT_recent_folders,
    FILEBROWSER_MT_bookmark_folders,
    FILEBROWSER_PT_quick_navigation,
)


register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                    
            