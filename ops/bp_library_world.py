import bpy
import os
import codecs
import subprocess
from ..bp_lib import bp_utils
from ..bp_utils import utils_library


preview_collections = {}
preview_collections["world_categories"] = utils_library.create_image_preview_collection()
preview_collections["world_items"] = utils_library.create_image_preview_collection()

def get_library_path():
    return utils_library.get_world_library_path()

def enum_world_categories(self,context):
    if context is None:
        return []

    icon_dir = get_library_path()
    pcoll = preview_collections["world_categories"]
    return utils_library.get_folder_enum_previews(icon_dir,pcoll)

def enum_world_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(get_library_path(),self.world_category)
    pcoll = preview_collections["world_items"]
    return utils_library.get_image_enum_previews(icon_dir,pcoll)

def update_world_category(self,context):
    if preview_collections["world_items"]:
        bpy.utils.previews.remove(preview_collections["world_items"])
        preview_collections["world_items"] = utils_library.create_image_preview_collection()
        
    enum_world_names(self,context)

def clear_world_categories(self,context):
    if preview_collections["world_categories"]:
        bpy.utils.previews.remove(preview_collections["world_categories"])
        preview_collections["world_categories"] = utils_library.create_image_preview_collection()

    enum_world_categories(self,context)

class LIBRARY_MT_world_library(bpy.types.Menu):
    bl_label = "World Library"

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        
        layout.operator('library.save_world_to_library',icon='BACK')
        layout.separator()
        layout.operator('bp_general.open_browser_window',icon='FILE_FOLDER').path = get_library_path()
        layout.operator('bp_general.create_new_folder',icon='NEWFOLDER').path = get_library_path()        
        layout.operator('library.change_world_library_path',icon='FILE_FOLDER')
        
class LIBRARY_OT_change_world_category(bpy.types.Operator):
    bl_idname = "library.change_world_category"
    bl_label = "Change World Category"

    category: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        props = utils_library.get_scene_props()
        props.active_world_library = self.category
        path = os.path.join(utils_library.get_active_library_path(props.library_tabs),props.active_world_library)
        if os.path.exists(path):
            utils_library.update_file_browser_path(context,path)
        return {'FINISHED'}

class LIBRARY_OT_change_world_library_path(bpy.types.Operator):
    bl_idname = "library.change_world_library_path"
    bl_label = "Change World Library Path"

    directory: bpy.props.StringProperty(subtype="DIR_PATH")
    
    def draw(self, context):
        pass

    def invoke(self, context, event):
        wm = context.window_manager
        if os.path.exists(get_library_path()):
            self.directory = get_library_path()
        wm.fileselect_add(self)      
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if os.path.exists(self.directory):
            wm = context.window_manager
            wm.bp_lib.world_library_path = self.directory
            clear_world_categories(self,context)
        return {'FINISHED'}


class LIBRARY_OT_drop_world_from_library(bpy.types.Operator):
    bl_idname = "library.drop_world_from_library"
    bl_label = "Drop World From Library"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")
    
    def execute(self, context):
        context.scene.world = self.get_world(context)
        context.area.tag_redraw()
        return {'FINISHED'}

    def get_world(self,context):
        path, ext = os.path.splitext(self.filepath)
        world_file_path = os.path.join(path + ".blend")
        with bpy.data.libraries.load(world_file_path, False, False) as (data_from, data_to):
            for world in data_from.worlds:
                data_to.worlds = [world]
                break
        for world in data_to.worlds:
            return world


class LIBRARY_OT_add_world_from_library(bpy.types.Operator):
    bl_idname = "library.add_world_from_library"
    bl_label = "Add World From Library"
    
    world_name: bpy.props.StringProperty(name="World Name")
    world_category: bpy.props.EnumProperty(name="World Category",items=enum_world_categories,update=update_world_category)
    world_name: bpy.props.EnumProperty(name="World Name",items=enum_world_names)
    
    world = None
    
    @classmethod
    def poll(cls, context):
        return True

    def check(self, context):
        wm = context.window_manager
        wm_props = wm.bp_lib
        if self.world_category != "":
            wm_props.world_category = self.world_category
        return True

    def invoke(self,context,event):
        clear_world_categories(self,context)
        update_world_category(self,context)
        wm = context.window_manager
        wm_props = wm.bp_lib
        if wm_props.world_category != "":
            self.world_category = wm_props.world_category              
        return wm.invoke_props_dialog(self, width=200 if len(self.world_category) > 0 else 300)
        
    def draw(self, context):
        layout = self.layout
        if len(self.world_category) == 0:
            layout.label(text="No Assets Found",icon='ERROR')
            layout.label(text="Use the menu to the right to save assets.")
        else:
            layout.prop(self,'world_category',text="",icon='FILE_FOLDER')  
            if len(self.world_name) > 0:
                layout.template_icon_view(self,"world_name",show_labels=True)  
                layout.label(text=self.world_name)
            else:
                layout.label(text="No Worlds Found In Category")
        
    def execute(self, context):
        context.scene.world = self.get_world(context)
        context.area.tag_redraw()
        return {'FINISHED'}

    def get_world(self,context):
        world_file_path = os.path.join(get_library_path() ,self.world_category,self.world_name + ".blend")
        with bpy.data.libraries.load(world_file_path, False, False) as (data_from, data_to):
            for world in data_from.worlds:
                if world == self.world_name:
                    data_to.worlds = [world]
                    break
        for world in data_to.worlds:
            return world

class LIBRARY_OT_save_world_to_library(bpy.types.Operator):
    bl_idname = "library.save_world_to_library"
    bl_label = "Save World to Library"
    
    world_name: bpy.props.StringProperty(name="World Name")
    world_category: bpy.props.EnumProperty(name="World Category",items=enum_world_categories,update=update_world_category)
    save_file: bpy.props.BoolProperty(name="Save File")
    create_new_category: bpy.props.BoolProperty(name="Create New Category")
    new_category_name: bpy.props.StringProperty(name="New Category Name")
    
    world = None
    
    @classmethod
    def poll(cls, context):
        return True

    def check(self, context):
        return True

    def invoke(self,context,event):
        clear_world_categories(self,context)
        self.world_name = context.scene.world.name
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)
        
    def draw(self, context):
        layout = self.layout

        if self.create_new_category:
            path = os.path.join(get_library_path() ,self.new_category_name) 
        else:
            path = os.path.join(get_library_path() ,self.world_category) 
        files = os.listdir(path) if os.path.exists(path) else []

        if self.create_new_category or len(self.world_category) == 0:
            row = layout.split(factor=.6)
            row.label(text="Enter new folder name:",icon='FILE_FOLDER')
            if len(self.world_category) > 0:
                row.prop(self,'create_new_category',text="Create New",icon='NEWFOLDER')
            layout.prop(self,'new_category_name',text="",icon='FILE_FOLDER')
            if self.new_category_name == "":
                layout.label(text="You must provide a category name",icon='ERROR')
            else:
                layout.label(text="") #DONT ADJUST INTERFACE
        else:
            row = layout.split(factor=.6)
            row.label(text="Select folder to save to:",icon='FILE_FOLDER')
            row.prop(self,'create_new_category',text="Create New",icon='NEWFOLDER')
            layout.prop(self,'world_category',text="",icon='FILE_FOLDER')
            
        layout.label(text="World Name: " + self.world_name)
        
        if self.world_name + ".blend" in files or self.world_name + ".png" in files:
            layout.label(text="File already exists",icon="ERROR")
        
    def create_world_thumbnail_script(self,source_dir,source_file,world_name):
        file = codecs.open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    for world in data_from.worlds:\n")
        file.write("        if world == '" + world_name + "':\n")
        file.write("            data_to.worlds = [world]\n")
        file.write("            break\n")
        file.write("for world in data_to.worlds:\n")
        file.write("    bpy.context.scene.world = world\n")
        file.write("    bpy.context.scene.camera.data.type = 'PANO'\n")
        file.write("    bpy.context.scene.camera.data.cycles.panorama_type = 'EQUIRECTANGULAR'\n")
        file.write("    bpy.context.scene.render.film_transparent = False\n")
        file.write("    render = bpy.context.scene.render\n")
        file.write("    render.use_file_extension = True\n")
        file.write("    render.filepath = r'" + os.path.join(source_dir,world_name) + "'\n")
        file.write("    bpy.ops.render.render(write_still=True)\n")
        
        file.close()
        
        return os.path.join(bpy.app.tempdir,'thumb_temp.py')
        
    def create_world_save_script(self,source_dir,source_file,world_name):
        file = codecs.open(os.path.join(bpy.app.tempdir,"save_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("import os\n")
        file.write("for mat in bpy.data.materials:\n")
        file.write("    bpy.data.materials.remove(mat,do_unlink=True)\n")
        file.write("for obj in bpy.data.objects:\n")
        file.write("    bpy.data.objects.remove(obj,do_unlink=True)\n")        
        file.write("for world in bpy.data.worlds:\n")
        file.write("    bpy.data.worlds.remove(world,do_unlink=True)\n")            
        file.write("bpy.context.preferences.filepaths.save_version = 0\n")
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    for world in data_from.worlds:\n")
        file.write("        if world == '" + world_name + "':\n")
        file.write("            data_to.worlds = [world]\n")
        file.write("            break\n")
        file.write("for world in data_to.worlds:\n")
        file.write("    bpy.context.scene.world = world\n")
        file.write("bpy.ops.wm.save_as_mainfile(filepath=r'" + os.path.join(source_dir,world_name) + ".blend')\n")
        file.close()
        
        return os.path.join(bpy.app.tempdir,'save_temp.py')        
        
    def execute(self, context):
        if bpy.data.filepath == "":
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(bpy.app.tempdir,"temp_blend.blend"))
        
        world_to_save = context.scene.world
        if self.create_new_category or len(self.world_category) == 0:
            if not os.path.exists(os.path.join(get_library_path() ,self.new_category_name)):
                os.makedirs(os.path.join(get_library_path() ,self.new_category_name))
            
            directory_to_save_to = os.path.join(get_library_path() ,self.new_category_name) 
        else:
            directory_to_save_to = os.path.join(get_library_path() ,self.world_category)         
        
        thumbnail_script_path = self.create_world_thumbnail_script(directory_to_save_to, bpy.data.filepath, world_to_save.name)
        save_script_path = self.create_world_save_script(directory_to_save_to, bpy.data.filepath, world_to_save.name)

        # subprocess.Popen(r'explorer ' + bpy.app.tempdir)
        
        subprocess.call(bpy.app.binary_path + ' "' + utils_library.get_thumbnail_file_path() + '" -b --python "' + thumbnail_script_path + '"')   
        subprocess.call(bpy.app.binary_path + ' -b --python "' + save_script_path + '"')
        
        # os.remove(thumbnail_script_path)
        # os.remove(save_script_path)
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(LIBRARY_MT_world_library)
    bpy.utils.register_class(LIBRARY_OT_drop_world_from_library)
    bpy.utils.register_class(LIBRARY_OT_change_world_category)
    bpy.utils.register_class(LIBRARY_OT_add_world_from_library)
    bpy.utils.register_class(LIBRARY_OT_save_world_to_library)
    bpy.utils.register_class(LIBRARY_OT_change_world_library_path)
    
def unregister():
    bpy.utils.unregister_class(LIBRARY_MT_world_library)
    bpy.utils.unregister_class(LIBRARY_OT_drop_world_from_library)
    bpy.utils.unregister_class(LIBRARY_OT_change_world_category)
    bpy.utils.unregister_class(LIBRARY_OT_add_world_from_library)
    bpy.utils.unregister_class(LIBRARY_OT_save_world_to_library)
    bpy.utils.unregister_class(LIBRARY_OT_change_world_library_path)
    