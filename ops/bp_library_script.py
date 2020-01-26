import bpy
import os
import subprocess
from ..bp_lib import bp_utils
from ..bp_utils import utils_library

class Script_Library_Item(bpy.types.PropertyGroup):
    package_name: bpy.props.StringProperty(name="Package Name")
    module_name: bpy.props.StringProperty(name="Module Name")
    class_name: bpy.props.StringProperty(name="Class Name")
    is_checked: bpy.props.BoolProperty(name="Is Checked")

class LIBRARY_OT_change_script_library(bpy.types.Operator):
    bl_idname = "library.change_script_library"
    bl_label = "Change Script Library"

    library: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        props = utils_library.get_scene_props()
        props.active_script_library = self.library
        lib = utils_library.get_active_script_library()
        path = lib.library_path
        if os.path.exists(path):
            utils_library.update_file_browser_path(context,path)
        return {'FINISHED'}


class LIBRARY_OT_change_script_category(bpy.types.Operator):
    bl_idname = "library.change_script_category"
    bl_label = "Change Script Category"

    category: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        props = utils_library.get_scene_props()
        props.active_script_category = self.category
        lib = utils_library.get_active_script_library()
        path = os.path.join(lib.library_path,self.category)
        if os.path.exists(path):
            utils_library.update_file_browser_path(context,path)
        return {'FINISHED'}


class LIBRARY_OT_create_thumbnails_for_library(bpy.types.Operator):
    bl_idname = "library.create_thumbnails_for_library"
    bl_label = "Create Thumbnails for Library"
    
    library_items: bpy.props.CollectionProperty(name="Library Items",type=Script_Library_Item)

    # collection_name: bpy.props.StringProperty(name="Collection Name")
    # collection_category: bpy.props.EnumProperty(name="Object Category",items=enum_collection_categories,update=update_collection_category)
    # save_file: bpy.props.BoolProperty(name="Save File")
    # create_new_category: bpy.props.BoolProperty(name="Create New Category")
    # new_category_name: bpy.props.StringProperty(name="New Category Name")
    
    @classmethod
    def poll(cls, context):
        return True 

    def check(self, context):
        return True

    def create_collection_thumbnail_script(self,source_dir,source_file,collection_name):
        file = open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w')
        file.write("import bpy\n")
        #GET PACKAGE NAME OF CURRENT LIBRARY
        #GET CLASS NAME
        #CALL DRAW FUNCTION
        #CALL SETUP THUMBNAIL
        #RENDER

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
        props = utils_library.get_scene_props()
        lib = utils_library.get_active_script_library()

        for old_lib_item in self.library_items:
            self.library_items.remove(0)

        for library_item in lib.library_items:
            lib_item = self.library_items.add()
            lib_item.name = library_item.name
            lib_item.package_name = library_item.package_name
            lib_item.module_name = library_item.module_name
            lib_item.class_name = library_item.class_name

        #LOAD EACH LIBRARY ITEM INTO COLLECTION AND DETERMINE IF THUMBNAIL EXISTS
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)
        
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        for item in self.library_items:
            row = col.row()
            row.prop(item,'is_checked',text="")
            row.label(text=item.name)
        #DRAW EACH LIBRARY ITEM WITH CHECKBOX
        
    def execute(self, context):
        for item in self.library_items:
            print(item.package_name,item.module_name,item.class_name)

        #FOR EACH CHECKED ITEM 
        #PASS CLASS NAME TO FUNCTION TO WRITE SCRIPT

#         # if bpy.data.filepath == "":
#         #     bpy.ops.wm.save_as_mainfile(filepath=os.path.join(bpy.app.tempdir,"temp_blend.blend"))
                    
#         collection_to_save = context.view_layer.active_layer_collection.collection
#         if self.create_new_category or len(self.collection_category) == 0:
#             if not os.path.exists(os.path.join(get_library_path() ,self.new_category_name)):
#                 os.makedirs(os.path.join(get_library_path() ,self.new_category_name))
            
#             directory_to_save_to = os.path.join(get_library_path() ,self.new_category_name) 
#         else:
#             directory_to_save_to = os.path.join(get_library_path() ,self.collection_category) 
            
        
#         thumbnail_script_path = self.create_collection_thumbnail_script(directory_to_save_to, bpy.data.filepath, collection_to_save.name)
#         save_script_path = self.create_collection_save_script(directory_to_save_to, bpy.data.filepath, collection_to_save.name)

#         if not os.path.exists(bpy.app.tempdir):
#             os.makedirs(bpy.app.tempdir)

# #         subprocess.Popen(r'explorer ' + bpy.app.tempdir)
        
#         subprocess.call(bpy.app.binary_path + ' "' + utils_library.get_thumbnail_file_path() + '" -b --python "' + thumbnail_script_path + '"')   
#         subprocess.call(bpy.app.binary_path + ' -b --python "' + save_script_path + '"')
        
#         os.remove(thumbnail_script_path)
#         os.remove(save_script_path)        
        
        return {'FINISHED'}    

def register():
    bpy.utils.register_class(Script_Library_Item)
    bpy.utils.register_class(LIBRARY_OT_change_script_library)
    bpy.utils.register_class(LIBRARY_OT_change_script_category)
    bpy.utils.register_class(LIBRARY_OT_create_thumbnails_for_library)
    
    
def unregister():
    bpy.utils.unregister_class(Script_Library_Item)
    bpy.utils.unregister_class(LIBRARY_OT_change_script_library)
    bpy.utils.unregister_class(LIBRARY_OT_change_script_category)
    bpy.utils.unregister_class(LIBRARY_OT_create_thumbnails_for_library)