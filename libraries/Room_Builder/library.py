import bpy
import math
from .bp_lib import bp_types, bp_unit, bp_utils
import time
from . import base_classes

class Stud(base_classes.Part):
    show_in_library = True

    def draw(self):
        start_time = time.time()
        self.create_assembly("Stud")

        self.obj_x.location.x = bp_unit.inch(120) #Length
        self.obj_y.location.y = bp_unit.inch(4)   #Depth
        self.obj_z.location.z = bp_unit.inch(2)   #Thickness

        quantity = self.obj_prompts.prompt_page.add_prompt('QUANTITY',"Quantity")
        array_offset = self.obj_prompts.prompt_page.add_prompt('DISTANCE',"Array Offset")
        quantity.set_value(1)
        array_offset.set_value(bp_unit.inch(16))

        qty = quantity.get_var("qty")
        array_offset = array_offset.get_var("array_offset")

        #When assigning vertices to a hook the transformation is made so the size must be 0
        # size = (self.obj_x.location.x,self.obj_y.location.y,self.obj_z.location.z)
        size = (0,0,0)
        obj_mesh = bp_utils.create_cube_mesh("Bottom Plate",size)
        self.add_object(obj_mesh)

        vgroup = obj_mesh.vertex_groups[self.obj_x.name]
        vgroup.add([2,3,6,7],1,'ADD')        

        vgroup = obj_mesh.vertex_groups[self.obj_y.name]
        vgroup.add([1,2,5,6],1,'ADD')

        vgroup = obj_mesh.vertex_groups[self.obj_z.name]
        vgroup.add([4,5,6,7],1,'ADD')        

        hook = obj_mesh.modifiers.new('XHOOK','HOOK')
        hook.object = self.obj_x
        hook.vertex_indices_set([2,3,6,7])

        hook = obj_mesh.modifiers.new('YHOOK','HOOK')
        hook.object = self.obj_y
        hook.vertex_indices_set([1,2,5,6])

        hook = obj_mesh.modifiers.new('ZHOOK','HOOK')
        hook.object = self.obj_z
        hook.vertex_indices_set([4,5,6,7])

        array = obj_mesh.modifiers.new('Quantity','ARRAY')
        array.use_constant_offset = True
        array.use_relative_offset = False
        obj_mesh.drivers.modifier(array,'count',-1,'qty',[qty])
        obj_mesh.drivers.modifier(array,'constant_offset_displace',2,'array_offset',[array_offset])

        #THIS OPERATION TAKES THE LONGEST
        # obj_mesh.bp_props.hook_vertex_group_to_object(self.obj_x.name,self.obj_x)
        # obj_mesh.bp_props.hook_vertex_group_to_object(self.obj_y.name,self.obj_y)
        # obj_mesh.bp_props.hook_vertex_group_to_object(self.obj_z.name,self.obj_z)
        print("STUD: Draw Time --- %s seconds ---" % (time.time() - start_time))

class Wall(base_classes.Wall):
    show_in_library = True

    def draw(self):
        start_time = time.time()
        #Create Assembly
        self.create_assembly("Wall")

        #Set Default Dimensions
        self.obj_x.location.x = bp_unit.inch(120) #Length
        self.obj_y.location.y = bp_unit.inch(8)   #Thickness
        self.obj_z.location.z = bp_unit.inch(96)  #Height

        #Figure out how to run operators from draw function
        # bpy.ops.mesh.primitive_circle_add()
        # bpy.context.view_layer.objects.active.parent = self.obj_bp
        
        #Get Product Variables
        length = self.obj_x.drivers.get_var('location.x','length')
        wall_thickness = self.obj_y.drivers.get_var('location.y','wall_thickness')
        height = self.obj_z.drivers.get_var('location.z','height')

        #Add Prompts
        stud_spacing_distance = self.obj_prompts.prompt_page.add_prompt('DISTANCE',"Stud Spacing Distance")
        stud_spacing_distance.set_value(bp_unit.inch(16))

        material_thickness = self.obj_prompts.prompt_page.add_prompt('DISTANCE',"Material Thickness")
        material_thickness.set_value(bp_unit.inch(2))

        #Get Prompt Variables
        material_thickness = material_thickness.get_var("material_thickness")
        stud_spacing_distance = stud_spacing_distance.get_var("stud_spacing_distance")

        #Add Parts
        bottom_plate = self.add_assembly(Stud())
        bottom_plate.set_name('Bottom Plate')
        bottom_plate.loc_x(value=0)
        bottom_plate.loc_y(value=0)
        bottom_plate.loc_z(value=0)
        bottom_plate.dim_x('length',[length])
        bottom_plate.dim_y('wall_thickness',[wall_thickness])
        bottom_plate.dim_z('material_thickness',[material_thickness])

        top_plate = self.add_assembly(Stud())
        top_plate.set_name('Top Plate')
        top_plate.loc_x(value=0)
        top_plate.loc_y(value=0)
        top_plate.loc_z('height',[height])
        top_plate.dim_x('length',[length])
        top_plate.dim_y('wall_thickness',[wall_thickness])
        top_plate.dim_z('-material_thickness',[material_thickness])

        first_stud = self.add_assembly(Stud())
        first_stud.set_name('First Stud')
        first_stud.loc_x(value=0)
        first_stud.loc_y(value=0)
        first_stud.loc_z('material_thickness',[material_thickness])
        first_stud.rot_y(value=math.radians(-90))
        first_stud.dim_x('height-(material_thickness*2)',[height,material_thickness])
        first_stud.dim_y('wall_thickness',[wall_thickness])
        first_stud.dim_z('-material_thickness',[material_thickness])

        last_stud = self.add_assembly(Stud())
        last_stud.set_name('Last Stud')
        last_stud.loc_x('length',[length])
        last_stud.loc_y(value=0)
        last_stud.loc_z('material_thickness',[material_thickness])
        last_stud.rot_y(value=math.radians(-90))
        last_stud.dim_x('height-(material_thickness*2)',[height,material_thickness])
        last_stud.dim_y('wall_thickness',[wall_thickness])
        last_stud.dim_z('material_thickness',[material_thickness])

        center_stud = self.add_assembly(Stud())
        center_stud.set_name('Center Stud')
        center_stud.loc_x('stud_spacing_distance',[stud_spacing_distance])
        center_stud.loc_y(value=0)
        center_stud.loc_z('material_thickness',[material_thickness])
        center_stud.rot_y(value=math.radians(-90))
        center_stud.dim_x('height-(material_thickness*2)',[height,material_thickness])
        center_stud.dim_y('wall_thickness',[wall_thickness])
        center_stud.dim_z('material_thickness',[material_thickness])

        qty = center_stud.get_prompt('Quantity')
        offset = center_stud.get_prompt('Array Offset')

        qty.set_formula('(length-material_thickness)/stud_spacing_distance',[length,material_thickness,stud_spacing_distance])
        offset.set_formula('-stud_spacing_distance',[stud_spacing_distance])  
             
        print("WALL: Draw Time --- %s seconds ---" % (time.time() - start_time))

class Room(base_classes.Room):
    show_in_library = True

    def draw(self):
        start_time = time.time()
        
        #Create Assembly
        self.create_assembly("Room")

        #ASSIGN PROPERTY
        self.coll["IS_ROOM"] = True

        #Set Default Dimensions
        self.obj_x.location.x = bp_unit.inch(120) #Length
        self.obj_y.location.y = bp_unit.inch(120) #Depth
        self.obj_z.location.z = bp_unit.inch(96) #Height

        #Get Product Variables
        length = self.obj_x.drivers.get_var('location.x','length')
        depth = self.obj_y.drivers.get_var('location.y','depth')
        height = self.obj_z.drivers.get_var('location.z','height')

        #Add Prompts
        wall_thickness = self.obj_prompts.prompt_page.add_prompt('DISTANCE',"Wall Thickness")

        #Set Prompt Formulas or default values
        wall_thickness.set_value(bp_unit.inch(4))

        #Get Prompt Variables
        wall_thickness = wall_thickness.get_var("wall_thickness")

        front_wall = self.add_assembly(Wall())
        front_wall.set_name("Front Wall")
        front_wall.loc_x(value=0)
        front_wall.loc_y(value=0)
        front_wall.loc_z(value=0)
        front_wall.rot_z(value=math.radians(0))
        front_wall.dim_x('length',[length])
        front_wall.dim_y('wall_thickness',[wall_thickness])
        front_wall.dim_z('height',[height])

        back_wall = self.add_assembly(Wall())
        back_wall.set_name("Back Wall")
        back_wall.loc_x(value=0)
        back_wall.loc_y('depth-wall_thickness',[depth,wall_thickness])
        back_wall.loc_z(value=0)
        back_wall.rot_z(value=math.radians(0))
        back_wall.dim_x('length',[length])
        back_wall.dim_y('wall_thickness',[wall_thickness])
        back_wall.dim_z('height',[height])

        left_wall = self.add_assembly(Wall())
        left_wall.set_name("Left Wall")
        left_wall.loc_x('length',[length])
        left_wall.loc_y('wall_thickness',[wall_thickness])
        left_wall.loc_z(value=0)
        left_wall.rot_z(value=math.radians(90))
        left_wall.dim_x('depth-(wall_thickness*2)',[depth,wall_thickness])
        left_wall.dim_y('wall_thickness',[wall_thickness])
        left_wall.dim_z('height',[height])      

        right_wall = self.add_assembly(Wall())
        right_wall.set_name("Right Wall")
        right_wall.loc_x(value=0)
        right_wall.loc_y('wall_thickness',[wall_thickness])
        right_wall.loc_z(value=0)
        right_wall.rot_z(value=math.radians(90))
        right_wall.dim_x('depth-(wall_thickness*2)',[depth,wall_thickness])
        right_wall.dim_y('-wall_thickness',[wall_thickness])
        right_wall.dim_z('height',[height])            

        print("ROOM: Draw Time --- %s seconds ---" % (time.time() - start_time))