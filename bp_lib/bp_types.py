import bpy
from bpy.types import Header, Menu, Operator, PropertyGroup, Panel

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       BoolVectorProperty,
                       PointerProperty,
                       CollectionProperty,
                       EnumProperty)


class Mesh_Hook(PropertyGroup):
    pass
    #obj = PointerTOEmptyObject


class Assembly:

    coll = None
    obj_bp = None
    obj_x = None
    obj_y = None
    obj_z = None
    obj_prompts = None

    def __init__(self,collection=None):
        if collection:
            self.coll = collection
            for obj in collection.objects:
                if "obj_bp" in obj:
                    self.obj_bp = obj
                if "obj_x" in obj:
                    self.obj_x = obj
                if "obj_y" in obj:
                    self.obj_y = obj           
                if "obj_z" in obj:
                    self.obj_z = obj
                if "obj_prompts" in obj:
                    self.obj_prompts = obj                    

    def update_vector_groups(self):
        """ 
        This is used to add all of the vector groups to 
        an assembly this should be called everytime a new object
        is added to an assembly.
        """
        vgroupslist = []
        objlist = []
        
        for child in self.obj_bp.children:
            if child.type == 'EMPTY' and 'obj_prompts' not in child:
                vgroupslist.append(child.name)
            if child.type == 'MESH':
                objlist.append(child)
        
        for obj in objlist:
            for vgroup in vgroupslist:
                if vgroup not in obj.vertex_groups:
                    obj.vertex_groups.new(name=vgroup)

    def create_assembly(self,assembly_name="New Assembly"):
        """ 
        This creates the basic structure for an assembly.
        This must be called first when creating an assembly from a script.
        """
        bpy.ops.object.select_all(action='DESELECT')

        layer_collection = bpy.context.view_layer.active_layer_collection
        coll = bpy.data.collections.new(assembly_name)
        layer_collection.collection.children.link(coll)
        bpy.ops.bp_collection.set_active_collection(collection_name=coll.name)

        self.coll = coll
        coll["IS_ASSEMBLY"] = True

        self.obj_bp = bpy.data.objects.new("OBJ_BP",None)
        self.obj_bp.location = (0,0,0)
        self.obj_bp["obj_bp"] = True
        self.obj_bp.empty_display_type = 'CUBE'
        self.obj_bp.empty_display_size = .1           
        coll.objects.link(self.obj_bp)

        self.obj_x = bpy.data.objects.new("OBJ_X",None)
        self.obj_x.location = (0,0,0)
        self.obj_x.parent = self.obj_bp
        self.obj_x["obj_x"] = True
        self.obj_x.empty_display_type = 'SPHERE'
        self.obj_x.empty_display_size = .1  
        self.obj_x.lock_location[0] = False       
        self.obj_x.lock_location[1] = True
        self.obj_x.lock_location[2] = True
        self.obj_x.lock_rotation[0] = True     
        self.obj_x.lock_rotation[1] = True   
        self.obj_x.lock_rotation[2] = True      
        coll.objects.link(self.obj_x)

        self.obj_y = bpy.data.objects.new("OBJ_Y",None)
        self.obj_y.location = (0,0,0)
        self.obj_y.parent = self.obj_bp
        self.obj_y["obj_y"] = True
        self.obj_y.empty_display_type = 'SPHERE'
        self.obj_y.empty_display_size = .1     
        self.obj_y.lock_location[0] = True       
        self.obj_y.lock_location[1] = False
        self.obj_y.lock_location[2] = True
        self.obj_y.lock_rotation[0] = True     
        self.obj_y.lock_rotation[1] = True   
        self.obj_y.lock_rotation[2] = True                    
        coll.objects.link(self.obj_y)      

        self.obj_z = bpy.data.objects.new("OBJ_Z",None)
        self.obj_z.location = (0,0,0)
        self.obj_z.parent = self.obj_bp
        self.obj_z["obj_z"] = True
        self.obj_z.empty_display_type = 'SINGLE_ARROW'
        self.obj_z.empty_display_size = .2     
        self.obj_z.lock_location[0] = True
        self.obj_z.lock_location[1] = True
        self.obj_z.lock_location[2] = False
        self.obj_z.lock_rotation[0] = True     
        self.obj_z.lock_rotation[1] = True   
        self.obj_z.lock_rotation[2] = True               
        coll.objects.link(self.obj_z)

        self.obj_prompts = bpy.data.objects.new("OBJ_PROMPTS",None)
        self.obj_prompts.location = (0,0,0)
        self.obj_prompts.parent = self.obj_bp
        self.obj_prompts.empty_display_size = 0      
        self.obj_prompts.lock_location[0] = True
        self.obj_prompts.lock_location[1] = True
        self.obj_prompts.lock_location[2] = True
        self.obj_prompts.lock_rotation[0] = True     
        self.obj_prompts.lock_rotation[1] = True   
        self.obj_prompts.lock_rotation[2] = True           
        self.obj_prompts["obj_prompts"] = True

        coll.objects.link(self.obj_prompts)

    def add_empty(self,obj_name):
        self.obj = bpy.data.objects.new(obj_name,None)
        self.obj.location = (0,0,0)
        self.obj.parent = self.obj_bp
        self.coll.objects.link(self.obj)

    def add_object(self,obj):
        obj.location = (0,0,0)
        obj.parent = self.obj_bp
        self.coll.objects.link(obj)
        self.update_vector_groups()
