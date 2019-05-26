import bpy
import math
from .bp_lib import bp_types, bp_unit, bp_utils
import time

class Stud(bp_types.Assembly):
    show_in_library = False

    def draw(self):
        start_time = time.time()
        self.create_assembly("Stud")

        self.obj_x.location.x = bp_unit.inch(120) #Length
        self.obj_y.location.y = bp_unit.inch(4)   #Depth
        self.obj_z.location.z = bp_unit.inch(2)   #Thickness

        size = (self.obj_x.location.x,self.obj_y.location.y,self.obj_z.location.z)
        obj_mesh = bp_utils.create_cube_mesh("Bottom Plate",size)
        self.add_object(obj_mesh)

        vgroup = obj_mesh.vertex_groups[self.obj_x.name]
        vgroup.add([2,3,6,7],1,'ADD')        

        vgroup = obj_mesh.vertex_groups[self.obj_y.name]
        vgroup.add([1,2,5,6],1,'ADD')

        vgroup = obj_mesh.vertex_groups[self.obj_z.name]
        vgroup.add([4,5,6,7],1,'ADD')        

        #THIS OPERATION TAKES THE LONGEST
        obj_mesh.bp_props.hook_vertex_group_to_object(self.obj_x.name,self.obj_x)
        obj_mesh.bp_props.hook_vertex_group_to_object(self.obj_y.name,self.obj_y)
        obj_mesh.bp_props.hook_vertex_group_to_object(self.obj_z.name,self.obj_z)
        print("STUD: Draw Time --- %s seconds ---" % (time.time() - start_time))

class Wall(bp_types.Assembly):
    show_in_library = True

    def draw(self):
        start_time = time.time()
        #Create Assembly
        self.create_assembly("Wall")

        #Set Default Dimensions
        self.obj_x.location.x = bp_unit.inch(120) #Length
        self.obj_y.location.y = bp_unit.inch(8)   #Thickness
        self.obj_z.location.z = bp_unit.inch(96)  #Height

        #Get Product Variables
        length = self.obj_x.drivers.get_var('location.x','length')
        wall_thickness = self.obj_y.drivers.get_var('location.y','wall_thickness')
        height = self.obj_z.drivers.get_var('location.z','height')

        #Add Prompts
        material_thickness = self.obj_prompts.prompt_page.add_prompt('DISTANCE',"Material Thickness")
        material_thickness.set_value(bp_unit.inch(2))

        #Get Prompt Variables
        material_thickness = material_thickness.get_var("material_thickness")

        #Add Parts
        bottom_plate = self.add_assembly(Stud())
        bottom_plate.obj_bp.location.x = 0
        bottom_plate.obj_bp.location.y = 0
        bottom_plate.obj_bp.location.z = 0
        bottom_plate.obj_x.drivers.x_loc('length',[length])
        bottom_plate.obj_y.drivers.y_loc('wall_thickness',[wall_thickness])
        bottom_plate.obj_z.drivers.z_loc('material_thickness',[material_thickness])

        bottom_plate = self.add_assembly(Stud())
        bottom_plate.obj_bp.drivers.z_loc('height',[height])
        bottom_plate.obj_bp.location.y = 0
        bottom_plate.obj_bp.location.z = 0
        bottom_plate.obj_x.drivers.x_loc('length',[length])
        bottom_plate.obj_y.drivers.y_loc('wall_thickness',[wall_thickness])
        bottom_plate.obj_z.drivers.z_loc('-material_thickness',[material_thickness])

        first_stud = self.add_assembly(Stud())
        first_stud.obj_bp.drivers.z_loc('material_thickness',[material_thickness])
        first_stud.obj_bp.location.y = 0
        first_stud.obj_bp.location.z = 0
        first_stud.obj_bp.rotation_euler.y = math.radians(-90)
        first_stud.obj_x.drivers.x_loc('height-(material_thickness*2)',[height,material_thickness])
        first_stud.obj_y.drivers.y_loc('wall_thickness',[wall_thickness])
        first_stud.obj_z.drivers.z_loc('-material_thickness',[material_thickness])

        last_stud = self.add_assembly(Stud())
        last_stud.obj_bp.drivers.x_loc('length',[length])
        last_stud.obj_bp.location.y = 0
        last_stud.obj_bp.drivers.z_loc('material_thickness',[material_thickness])
        last_stud.obj_bp.rotation_euler.y = math.radians(-90)
        last_stud.obj_x.drivers.x_loc('height-(material_thickness*2)',[height,material_thickness])
        last_stud.obj_y.drivers.y_loc('wall_thickness',[wall_thickness])
        last_stud.obj_z.drivers.z_loc('material_thickness',[material_thickness])
        print("WALL: Draw Time --- %s seconds ---" % (time.time() - start_time))

class Room(bp_types.Assembly):
    show_in_library = True

    def draw(self):
        start_time = time.time()
        #Create Assembly
        self.create_assembly("Room")

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
        front_wall.obj_bp.location.x = 0
        front_wall.obj_bp.location.y = 0
        front_wall.obj_bp.location.z = 0
        front_wall.obj_bp.rotation_euler.z = math.radians(0)
        front_wall.obj_x.drivers.x_loc('length',[length])
        front_wall.obj_y.drivers.y_loc('wall_thickness',[wall_thickness])
        front_wall.obj_z.drivers.z_loc('height',[height])

        back_wall = self.add_assembly(Wall())
        back_wall.obj_bp.location.x = 0
        back_wall.obj_bp.drivers.y_loc('depth-wall_thickness',[depth,wall_thickness])
        back_wall.obj_bp.location.z = 0
        back_wall.obj_bp.rotation_euler.z = math.radians(0)
        back_wall.obj_x.drivers.x_loc('length',[length])
        back_wall.obj_y.drivers.y_loc('wall_thickness',[wall_thickness])
        back_wall.obj_z.drivers.z_loc('height',[height])

        left_wall = self.add_assembly(Wall())
        left_wall.obj_bp.drivers.x_loc('length',[length])
        left_wall.obj_bp.drivers.y_loc('wall_thickness',[wall_thickness])
        left_wall.obj_bp.location.z = 0
        left_wall.obj_bp.rotation_euler.z = math.radians(90)
        left_wall.obj_x.drivers.x_loc('depth-(wall_thickness*2)',[depth,wall_thickness])
        left_wall.obj_y.drivers.y_loc('wall_thickness',[wall_thickness])
        left_wall.obj_z.drivers.z_loc('height',[height])      

        right_wall = self.add_assembly(Wall())
        right_wall.obj_bp.location.x = 0
        right_wall.obj_bp.drivers.y_loc('wall_thickness',[wall_thickness])
        right_wall.obj_bp.location.z = 0
        right_wall.obj_bp.rotation_euler.z = math.radians(90)
        right_wall.obj_x.drivers.x_loc('depth-(wall_thickness*2)',[depth,wall_thickness])
        right_wall.obj_y.drivers.y_loc('-wall_thickness',[wall_thickness])
        right_wall.obj_z.drivers.z_loc('height',[height])            

        print("ROOM: Draw Time --- %s seconds ---" % (time.time() - start_time))