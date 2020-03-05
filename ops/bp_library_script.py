import bpy
import os
import codecs
import subprocess
from ..bp_lib import bp_utils
from ..bp_utils import utils_library

class Script_Library_Item(bpy.types.PropertyGroup):
    package_name: bpy.props.StringProperty(name="Package Name")
    module_name: bpy.props.StringProperty(name="Module Name")
    class_name: bpy.props.StringProperty(name="Class Name")
    category_name: bpy.props.StringProperty(name="Category Name")
    is_checked: bpy.props.BoolProperty(name="Is Checked")


class LIBRARY_OT_drop_script_from_library(bpy.types.Operator):
    bl_idname = "library.drop_script_from_library"
    bl_label = "Drop Script from Library"

    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    def execute(self, context):
        dir, file = os.path.split(self.filepath)    
        path, category_name = os.path.split(dir)
        filename, ext = os.path.splitext(file)

        lib = utils_library.get_active_script_library()

        for item in lib.library_items:
            if item.category_name == category_name and item.name == filename:
                pkg = __import__(item.package_name)
                item = eval("pkg." + item.module_name + "." + item.class_name + "()")
                if hasattr(item,"draw"):
                    item.draw()

                if hasattr(item,"placement_id") and item.placement_id != "":
                    if item.obj_bp:
                        eval('bpy.ops.' + item.placement_id + '("INVOKE_DEFAULT",obj_bp_name=item.obj_bp.name,filepath=self.filepath)')
                    else:
                        eval('bpy.ops.' + item.placement_id + '("INVOKE_DEFAULT",filepath=self.filepath)')


        return {'FINISHED'}


class LIBRARY_OT_change_script_library(bpy.types.Operator):
    bl_idname = "library.change_script_library"
    bl_label = "Change Script Library"

    library: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        props = utils_library.get_scene_props()
        props.active_script_library = self.library

        lib = utils_library.get_active_script_library()
        folders = utils_library.get_active_categories(props.library_tabs)
        category = utils_library.get_active_category(props,folders)

        path = os.path.join(lib.library_path,category)
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
    build_asset: bpy.props.BoolProperty(name="Build Asset",default=False)
    
    @classmethod
    def poll(cls, context):
        return True 

    def check(self, context):
        return True

    def create_item_thumbnail_script(self,library_item):
        file = codecs.open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("import os\n")

        #GET SAVE PATH AND MAKE DIR
        file.write("pkg = __import__('" + library_item.package_name + "')\n")
        file.write("dir_path = os.path.join(pkg.LIBRARY_PATH,'" + library_item.category_name + "')\n")
        file.write("path = os.path.join(dir_path,'" + library_item.name + "')\n")
        file.write("if not os.path.exists(dir_path):\n")
        file.write("    os.makedirs(dir_path)\n")

        #SELECT ALL OBJECTS FUNCTION
        file.write("def select_collection_objects(coll):\n")
        file.write("    for obj in coll.objects:\n")
        file.write("        obj.select_set(True)\n")
        file.write("    for child in coll.children:\n")
        file.write("        select_collection_objects(child)\n")

        #CLEAR FILE
        file.write("for mat in bpy.data.materials:\n")
        file.write("    bpy.data.materials.remove(mat,do_unlink=True)\n")
        file.write("for obj in bpy.data.objects:\n")
        file.write("    bpy.data.objects.remove(obj,do_unlink=True)\n")   

        #DRAW ASSET
        file.write("item = eval('pkg." + library_item.module_name + "." + library_item.class_name + "()')" + "\n")
        file.write("if hasattr(item,'draw'):\n")
        file.write("    item.draw()\n")
        file.write("if hasattr(item,'render'):\n")
        file.write("    item.render()\n")        
        file.write("path = os.path.join(pkg.LIBRARY_PATH,'" + library_item.category_name + "','" + library_item.name + "')\n")

        #IF BUILD THEN CALL SAVE OPERATOR BEFORE SETTING UP THUMBNAIL DATA
        if self.build_asset:
            file.write("bpy.ops.wm.save_as_mainfile(filepath=path + '.blend')\n")

        #ADD CAMERA
        file.write("if bpy.context.scene.camera is None:\n")
        file.write("    bpy.ops.object.camera_add()\n")
        file.write("bpy.context.scene.camera = bpy.context.object\n")
        file.write("bpy.context.scene.camera.rotation_euler = (1.1093,0,.8149)\n")

        #ADD LIGHTING
        file.write("bpy.ops.object.light_add(type='SUN')\n")
        file.write("bpy.context.object.data.energy = 1.5\n")
        file.write("bpy.context.object.rotation_euler = (1.1093,0,.8149)\n")

        #SELECT AND VIEW ASSEMBLY
        file.write("if item.coll:\n")
        file.write("    select_collection_objects(item.coll)\n")
        file.write("bpy.ops.view3d.camera_to_view_selected()\n")

        #TODO: SETUP CUSTOM RENDERING FUNCTIONALITY WITH OPERATOR
        #file.write("if item.render_id != "":\n")
        #   eval('bpy.ops.' + item.render_id + '("INVOKE_DEFAULT",object_name=self.product.obj_bp.name)')

        #TODO: SETUP CUSTOM RENDERING FUNCTIONALITY WITH FUNCTION
        #file.write("if hasattr(item,'render'):\n")
        #   file.write("    item.render()\n")

        #RENDER
        file.write("render = bpy.context.scene.render\n")
        file.write("render.resolution_x = 540\n")
        file.write("render.resolution_y = 540\n")
        file.write("render.engine = 'BLENDER_EEVEE'\n")
        file.write("bpy.context.scene.eevee.use_gtao = True\n")
        file.write("bpy.context.scene.eevee.use_ssr = True\n")
        file.write("render.film_transparent = True\n")        
        file.write("render.use_file_extension = True\n")
        file.write("render.filepath = path\n")
        file.write("bpy.ops.render.render(write_still=True)\n")        
        file.close()
        return os.path.join(bpy.app.tempdir,'thumb_temp.py')
        
    def invoke(self,context,event):
        props = utils_library.get_scene_props()
        lib = utils_library.get_active_script_library()

        for old_lib_item in self.library_items:
            self.library_items.remove(0)

        for library_item in lib.library_items:
            lib_item = self.library_items.add()
            lib_item.name = library_item.name
            lib_item.category_name = library_item.category_name
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
            row.prop(item,'is_checked',text=item.name)
        
    def execute(self, context):
        for item in self.library_items:
            if item.is_checked:
                script = self.create_item_thumbnail_script(item)
                subprocess.call(bpy.app.binary_path + ' -b --python "' + script + '"') 

        return {'FINISHED'}

def register():
    bpy.utils.register_class(Script_Library_Item)
    bpy.utils.register_class(LIBRARY_OT_drop_script_from_library)
    bpy.utils.register_class(LIBRARY_OT_change_script_library)
    bpy.utils.register_class(LIBRARY_OT_change_script_category)
    bpy.utils.register_class(LIBRARY_OT_create_thumbnails_for_library)
    
    
def unregister():
    bpy.utils.unregister_class(Script_Library_Item)
    bpy.utils.unregister_class(LIBRARY_OT_drop_script_from_library)
    bpy.utils.unregister_class(LIBRARY_OT_change_script_library)
    bpy.utils.unregister_class(LIBRARY_OT_change_script_category)
    bpy.utils.unregister_class(LIBRARY_OT_create_thumbnails_for_library)