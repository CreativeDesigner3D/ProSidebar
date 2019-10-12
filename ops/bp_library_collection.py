import bpy
import os
import subprocess
from ..bp_lib import bp_utils
from ..bp_utils import utils_library

COLLECTION_FOLDER = os.path.join(utils_library.LIBRARY_FOLDER,"collections")
preview_collections = {}
preview_collections["collection_categories"] = utils_library.create_image_preview_collection()
preview_collections["collection_items"] = utils_library.create_image_preview_collection()

def get_library_path():
    props = utils_library.get_wm_props()
    if os.path.exists(props.collection_library_path):
        return props.collection_library_path
    else:
        return COLLECTION_FOLDER
    
def enum_collection_categories(self,context):
    if context is None:
        return []
    
    icon_dir = get_library_path()
    pcoll = preview_collections["collection_categories"]
    return utils_library.get_folder_enum_previews(icon_dir,pcoll)

def enum_collection_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(get_library_path(),self.collection_category)
    pcoll = preview_collections["collection_items"]
    return utils_library.get_image_enum_previews(icon_dir,pcoll)

def update_collection_category(self,context):
    if preview_collections["collection_items"]:
        bpy.utils.previews.remove(preview_collections["collection_items"])
        preview_collections["collection_items"] = utils_library.create_image_preview_collection()     
        
    enum_collection_names(self,context)

def clear_collection_categories(self,context):
    if preview_collections["collection_categories"]:
        bpy.utils.previews.remove(preview_collections["collection_categories"])
        preview_collections["collection_categories"] = utils_library.create_image_preview_collection()

    enum_collection_categories(self,context)

class LIBRARY_MT_collection_library(bpy.types.Menu):
    bl_label = "Collection Library"

    def draw(self, context):
        layout = self.layout
        layout.operator('library.save_collection_to_library',icon='BACK')
        layout.separator()
        layout.operator('bp_general.open_browser_window',icon='FILE_FOLDER').path = get_library_path()
        layout.operator('bp_general.create_new_folder',icon='NEWFOLDER').path = get_library_path()        
        layout.operator('library.change_collection_library_path',icon='FILE_FOLDER')        

class LIBRARY_OT_change_collection_library_path(bpy.types.Operator):
    bl_idname = "library.change_collection_library_path"
    bl_label = "Change Collection Library Path"

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
            wm.bp_lib.collection_library_path = self.directory
            clear_collection_categories(self,context)
        return {'FINISHED'}

class LIBRARY_OT_add_collection_from_library(bpy.types.Operator):
    bl_idname = "library.add_collection_from_library"
    bl_label = "Add Collection From Library"
    
    obj_name: bpy.props.StringProperty(name="Obj Name")
    collection_category: bpy.props.EnumProperty(name="Collection Category",items=enum_collection_categories,update=update_collection_category)
    collection_name: bpy.props.EnumProperty(name="Collection Name",items=enum_collection_names)
    
    drawing_plane = None
    grp = None
    parent_obj_dict = {}
    collection_objects = []
    
    @classmethod
    def poll(cls, context):
        if context.object and context.object.mode != 'OBJECT':
            return False        
        return True

    def check(self, context):
        wm = context.window_manager
        wm_props = wm.bp_lib
        if self.collection_category != "":
            wm_props.collection_category = self.collection_category
        return True

    def invoke(self,context,event):
        self.collection_objects = []
        self.parent_obj_dict = {}
        clear_collection_categories(self,context)
        update_collection_category(self,context)
        wm = context.window_manager
        wm_props = wm.bp_lib
        if wm_props.collection_category != "":
            self.collection_category = wm_props.collection_category
        return wm.invoke_props_dialog(self, width=200)
        
    def draw(self, context):
        layout = self.layout
        layout.prop(self,'collection_category',text="",icon='FILE_FOLDER')  
        layout.template_icon_view(self,"collection_name",show_labels=True)  
        layout.label(text=self.collection_name)
        
    def execute(self, context):
        self.create_drawing_plane(context)
        self.grp = self.get_collection(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def get_collection_objects(self,coll):
        for obj in coll.objects:
            self.collection_objects.append(obj)
            if obj.parent is None:
                self.parent_obj_dict[obj] = (obj.location.x, obj.location.y, obj.location.z)

        for child in coll.children:
            self.get_collection_objects(child)

    def get_collection(self,context):
        collection_file_path = os.path.join(get_library_path() ,self.collection_category,self.collection_name + ".blend")
        with bpy.data.libraries.load(collection_file_path, False, False) as (data_from, data_to):
            
            for coll in data_from.collections:
                if coll == self.collection_name:
                    data_to.collections = [coll]
                    break
            
        for coll in data_to.collections:
            context.view_layer.active_layer_collection.collection.children.link(coll)
            self.get_collection_objects(coll)
            return coll

    def create_drawing_plane(self,context):
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.display_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)

    def position_collection(self,selected_point,selected_obj):
        for obj, location in self.parent_obj_dict.items():
            obj.location = selected_point
            obj.location.x += location[0]
            obj.location.y += location[1]
            obj.location.z += location[2]

    def modal(self, context, event):
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        selected_point, selected_obj = bp_utils.get_selection_point(context,event,exclude_objects=self.collection_objects)

        self.position_collection(selected_point,selected_obj)
        
        if self.event_is_place_collection(event):
            return self.finish(context)

        if self.event_is_cancel_command(event):
            return self.cancel_drop(context)
        
        if self.event_is_pass_through(event):
            return {'PASS_THROUGH'}        
        
        return {'RUNNING_MODAL'}

    def event_is_place_collection(self,event):
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            return True
        elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS':
            return True
        elif event.type == 'RET' and event.value == 'PRESS':
            return True
        else:
            return False

    def event_is_cancel_command(self,event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            return True
        else:
            return False
    
    def event_is_pass_through(self,event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return True
        else:
            return False

    def cancel_drop(self,context):
        obj_list = []
        obj_list.append(self.drawing_plane)
        for obj in self.collection_objects:
            obj_list.append(obj)
        bp_utils.delete_obj_list(obj_list)
        return {'CANCELLED'}
    
    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        if self.drawing_plane:
            bp_utils.delete_obj_list([self.drawing_plane])
        bpy.ops.object.select_all(action='DESELECT')
        for obj, location in self.parent_obj_dict.items():
            obj.select_set(True)  
            context.view_layer.objects.active = obj             
        #SELECT BASE POINTS
        context.area.tag_redraw()
        return {'FINISHED'}
    
class LIBRARY_OT_save_collection_to_library(bpy.types.Operator):
    bl_idname = "library.save_collection_to_library"
    bl_label = "Save Collection to Library"
    
    collection_name: bpy.props.StringProperty(name="Collection Name")
    collection_category: bpy.props.EnumProperty(name="Object Category",items=enum_collection_categories,update=update_collection_category)
    save_file: bpy.props.BoolProperty(name="Save File")
    create_new_category: bpy.props.BoolProperty(name="Create New Category")
    new_category_name: bpy.props.StringProperty(name="New Category Name")
    
    @classmethod
    def poll(cls, context):
        return True #FIGURE OUT WHAT IS ACTIVE
        # if context.scene.outliner.selected_collection_index + 1 <= len(bpy.data.collections):
        #     return True
        # else:
        #     return False

    def check(self, context):
        return True

    def select_collection_objects(self,coll):
        for obj in coll.objects:
            obj.select_set(True)
        for child in coll.children:
            self.select_collection_objects(child)

    def create_collection_thumbnail_script(self,source_dir,source_file,collection_name):
        file = open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w')
        file.write("import bpy\n")
        file.write("def select_collection_objects(coll):\n")
        file.write("    for obj in coll.objects:\n")
        file.write("        obj.select_set(True)\n")
        file.write("    for child in coll.children:\n")
        file.write("        select_collection_objects(child)\n")
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    for collection in data_from.collections:\n")
        file.write("        if collection == '" + collection_name + "':\n")
        file.write("            data_to.collections = [collection]\n")
        file.write("            break\n")
        file.write("for collection in data_to.collections:\n")
        file.write("    bpy.context.view_layer.active_layer_collection.collection.children.link(collection)\n")
        file.write("    select_collection_objects(collection)\n")
        # file.write("    for obj in collection.objects:\n")
        # file.write("        bpy.context.scene.objects.link(obj)\n") #TODO: FIX
        # file.write("        obj.select_set(True)\n")
        # file.write("        bpy.context.scene.objects.active = obj\n")
        file.write("    bpy.ops.view3d.camera_to_view_selected()\n")
        file.write("    render = bpy.context.scene.render\n")
        file.write("    render.use_file_extension = True\n")
        file.write("    render.filepath = r'" + os.path.join(source_dir,collection_name) + "'\n")
        file.write("    bpy.ops.render.render(write_still=True)\n")
        file.close()
        return os.path.join(bpy.app.tempdir,'thumb_temp.py')
        
    def create_collection_save_script(self,source_dir,source_file,collection_name):
        file = open(os.path.join(bpy.app.tempdir,"save_temp.py"),'w')
        file.write("import bpy\n")
        file.write("import os\n")
        file.write("for mat in bpy.data.materials:\n")
        file.write("    bpy.data.materials.remove(mat,do_unlink=True)\n")
        file.write("for obj in bpy.data.objects:\n")
        file.write("    bpy.data.objects.remove(obj,do_unlink=True)\n")               
        file.write("bpy.context.preferences.filepaths.save_version = 0\n") #TODO: FIX THIS
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    for collection in data_from.collections:\n")
        file.write("        if collection == '" + collection_name + "':\n")
        file.write("            data_to.collections = [collection]\n")
        file.write("            break\n")
        file.write("for collection in data_to.collections:\n")
        file.write("    bpy.context.view_layer.active_layer_collection.collection.children.link(collection)\n")
        file.write("bpy.ops.wm.save_as_mainfile(filepath=r'" + os.path.join(source_dir,collection_name) + ".blend')\n")
        file.close()
        return os.path.join(bpy.app.tempdir,'save_temp.py')

    def invoke(self,context,event):
        collection = context.view_layer.active_layer_collection.collection
        self.collection_name = collection.name
        clear_collection_categories(self,context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)
        
    def draw(self, context):
        layout = self.layout
        if self.create_new_category:
            path = os.path.join(get_library_path() ,self.new_category_name) 
        else:
            path = os.path.join(get_library_path() ,self.collection_category) 
        files = os.listdir(path) if os.path.exists(path) else []
        
        if self.create_new_category:
            row = layout.split(factor=.6)
            row.label(text="Enter new folder name:",icon='FILE_FOLDER')
            row.prop(self,'create_new_category',text="Create New",icon='NEWFOLDER')
            layout.prop(self,'new_category_name',text="",icon='FILE_FOLDER')
        else:
            row = layout.split(factor=.6)
            row.label(text="Select folder to save to:",icon='FILE_FOLDER')
            row.prop(self,'create_new_category',text="Create New",icon='NEWFOLDER')
            layout.prop(self,'collection_category',text="",icon='FILE_FOLDER')

        layout.label(text="Name: " + self.collection_name)
        if self.collection_name + ".blend" in files or self.collection_name + ".png" in files:
            layout.label(text="File already exists",icon="ERROR")

        if bpy.data.filepath != "" and bpy.data.is_dirty:
            row = layout.split(factor=.6)
            row.label(text="File is not saved",icon="ERROR")
            row.prop(self,'save_file',text="Auto Save")
        
    def execute(self, context):
        if bpy.data.filepath == "":
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(bpy.app.tempdir,"temp_blend.blend"))
                    
        collection_to_save = context.view_layer.active_layer_collection.collection
        if self.create_new_category:
            os.makedirs(os.path.join(get_library_path() ,self.new_category_name))
            
            directory_to_save_to = os.path.join(get_library_path() ,self.new_category_name) 
        else:
            directory_to_save_to = os.path.join(get_library_path() ,self.collection_category) 
            
        
        thumbnail_script_path = self.create_collection_thumbnail_script(directory_to_save_to, bpy.data.filepath, collection_to_save.name)
        save_script_path = self.create_collection_save_script(directory_to_save_to, bpy.data.filepath, collection_to_save.name)

        if not os.path.exists(bpy.app.tempdir):
            os.makedirs(bpy.app.tempdir)

#         subprocess.Popen(r'explorer ' + bpy.app.tempdir)
        
        subprocess.call(bpy.app.binary_path + ' "' + utils_library.get_thumbnail_file_path() + '" -b --python "' + thumbnail_script_path + '"')   
        subprocess.call(bpy.app.binary_path + ' -b --python "' + save_script_path + '"')
        
        os.remove(thumbnail_script_path)
        os.remove(save_script_path)        
        
        return {'FINISHED'}    
    
def register():
    bpy.utils.register_class(LIBRARY_MT_collection_library)
    bpy.utils.register_class(LIBRARY_OT_add_collection_from_library)
    bpy.utils.register_class(LIBRARY_OT_save_collection_to_library)
    bpy.utils.register_class(LIBRARY_OT_change_collection_library_path)

def unregister():
    bpy.utils.unregister_class(LIBRARY_MT_collection_library)
    bpy.utils.unregister_class(LIBRARY_OT_add_collection_from_library)
    bpy.utils.unregister_class(LIBRARY_OT_save_collection_to_library)
    bpy.utils.unregister_class(LIBRARY_OT_change_collection_library_path)
    