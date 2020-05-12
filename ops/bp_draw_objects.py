import bpy
import bmesh
import math
from bpy_extras import view3d_utils
import mathutils
from mathutils import Vector
from .. import sidebar_utils
from bpy_extras.view3d_utils import location_3d_to_region_2d

def get_point_under_mouse(context,event):
    viewport_region = context.region
    viewport_region_data = context.space_data.region_3d
    viewport_matrix = viewport_region_data.view_matrix.inverted()
    
    # Shooting a ray from the camera, through the mouse cursor towards the grid with a length of 100000
    # If the camera is more than 100000 units away from the grid it won't detect a point
    ray_start = viewport_matrix.to_translation()
    ray_depth = viewport_matrix @ Vector((0,0,-100000))
    
    # Get the 3D vector position of the mouse
    ray_end = view3d_utils.region_2d_to_location_3d(viewport_region,viewport_region_data, (event.mouse_region_x, event.mouse_region_y), ray_depth )
    
    # A triangle on the grid plane. We use these 3 points to define a plane on the grid
    point_1 = Vector((0,0,0))
    point_2 = Vector((0,1,0))
    point_3 = Vector((1,0,0))
    
    # Create a 3D position on the grid under the mouse cursor using the triangle as a grid plane
    # and the ray cast from the camera
    return mathutils.geometry.intersect_ray_tri(point_1,point_2,point_3,ray_end,ray_start,False )    

class BP_OT_draw_plane(bpy.types.Operator):
    bl_idname = "bp.draw_plane"
    bl_label = "Draw Plane"
    bl_options = {'UNDO'}
    
    #READONLY
    _draw_handle = None
    mouse_x = 0
    mouse_y = 0
    
    snapping_point_2d = (0,0,0)
    placement_point_3d = (0,0,0)
    
    drawing_plane = None
    cube = None
    plane = None
    ray_cast_objects = []
    placed_first_point = False
    first_point = (0,0,0)
    selected_point = (0,0,0)
    found_snap_point = False
    
    def cancel_drop(self,context):
        sidebar_utils.delete_object_and_children(self.plane)
        self.finish(context)
        
    def finish(self,context):
        # context.space_data.draw_handler_remove(self._draw_handle, 'WINDOW')
        context.window.cursor_set('DEFAULT')
        context.area.tag_redraw()
        return {'FINISHED'}

    # @staticmethod
    # def _window_region(context):
    #     window_regions = [region
    #                       for region in context.area.regions
    #                       if region.type == 'WINDOW']
    #     return window_regions[0]

    # def draw_opengl(self,context):     
    #     region = self._window_region(context)
        
        # if self.placed_first_point:
        #     help_text = "Command Help:\nLEFT CLICK: Place Second Point\nRIGHT CLICK: Cancel Command"
        # else:
        #     help_text = "Command Help:\nLEFT CLICK: Place First Point\nRIGHT CLICK: Cancel Command"
        
        # if self.found_snap_point:
        #     help_text += "\n SNAP TO VERTEX"
        
        # help_box = TextBox(
        #     x=0,y=0,
        #     width=500,height=0,
        #     border=10,margin=100,
        #     message=help_text)
        # help_box.x = (self.mouse_x + (help_box.width) / 2 + 10) - region.x
        # help_box.y = (self.mouse_y - 10) - region.y
        
        # help_box.draw()
        
        # # SNAP POINT
        # bgl.glPushAttrib(bgl.GL_ENABLE_BIT)
     
        # bgl.glColor4f(255, 0.0, 0.0, 1.0)
        # bgl.glEnable(bgl.GL_BLEND)
         
        # bgl.glPointSize(10)
        # bgl.glBegin(bgl.GL_POINTS)
     
        # if self.snapping_point_2d:
        #     bgl.glVertex2f(self.snapping_point_2d[0], self.snapping_point_2d[1])
     
        # bgl.glEnd()
        # bgl.glPopAttrib()
     
        # # restore opengl defaults
        # bgl.glDisable(bgl.GL_BLEND)
        # bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

    def event_is_place_first_point(self,event):
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and self.placed_first_point == False:
            return True
        elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS' and self.placed_first_point == False:
            return True
        elif event.type == 'RET' and event.value == 'PRESS' and self.placed_first_point == False:
            return True
        else:
            return False

    def event_is_place_second_point(self,event):
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and self.placed_first_point:
            return True
        elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS' and self.placed_first_point:
            return True
        elif event.type == 'RET' and event.value == 'PRESS' and self.placed_first_point:
            return True
        else:
            return False

    def calc_distance(self,point1,point2):
        """ This gets the distance between two points (X,Y,Z)
        """
        x1, y1, z1 = point1
        x2, y2, z2 = point2
        
        return math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2) 

    def get_snap_point(self,context,selected_point,selected_obj):
        """
            Used to set the self.snapping_point_2d for opengl and
            Used to set the self.placement_point_3d for final placement position
        """
        if selected_obj is not None:
            obj_data = selected_obj.to_mesh(bpy.context.scene, True, 'PREVIEW')
            mesh = obj_data
            size = len(mesh.vertices)
            kd = mathutils.kdtree.KDTree(size)
            for i, v in enumerate(mesh.vertices):
                kd.insert(selected_obj.matrix_world * v.co, i)
            kd.balance()
            snapping_point, index, dist = kd.find(selected_point)
            
            dist = self.calc_distance(snapping_point, selected_point)
            
            if dist > .5:
                #TOO FAR AWAY FROM SNAP POINT
                self.snapping_point_2d = location_3d_to_region_2d(context.region, 
                                                                  context.space_data.region_3d, 
                                                                  selected_point)
                self.placement_point_3d = selected_point
                self.found_snap_point = False
            else:
                #FOUND POINT TO SNAP TO
                self.snapping_point_2d = location_3d_to_region_2d(context.region, 
                                                                  context.space_data.region_3d, 
                                                                  snapping_point)
                self.placement_point_3d = snapping_point
                self.found_snap_point = True
                
            bpy.data.meshes.remove(obj_data)
        
    def position_cube(self,context,selected_point,selected_obj):
        # self.get_snap_point(context, selected_point, selected_obj)
        print("SELECTED POINT: ",selected_point,selected_obj)

        if not self.placed_first_point:
            self.plane.location = selected_point
            self.first_point = selected_point
            
        else:
            print('FIRST POINT: ',self.first_point,self.plane.location)
            for i, vert in enumerate(self.plane.data.vertices):
                
                if i == 0:
                    vert.co = (0,0,0)
                if i == 1:
                    vert.co = (selected_point[0] - self.first_point[0], 0, 0)
                if i == 2:
                    vert.co = (selected_point[0] - self.first_point[0], selected_point[1] - self.first_point[1], 0)
                if i == 3:
                    vert.co = (0,selected_point[1] - self.first_point[1], 0)
            
    def modal(self, context, event):
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        
        # Fix this to return Locations on Object if found
        hit_info = sidebar_utils.floor_raycast(context,self.mouse_x,self.mouse_y)

        #This works great for Grid in Perspective Mode not Orthographic!
        grid_location = get_point_under_mouse(context,event)

        if hit_info[5] == None:
            # context.scene.cursor.location = grid_location
            self.position_cube(context,grid_location,None)
        else:
            self.position_cube(context,hit_info[1],hit_info[5])

        if self.event_is_place_second_point(event):
            return self.finish(context)

        if self.event_is_place_first_point(event):
            self.placed_first_point = True

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel_drop(context)
            return {'CANCELLED'}
        
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}        
        
        return {'RUNNING_MODAL'}
        
    def create_drawing_plane(self,context):
        width = 0
        height = 0
        depth = 0
        
        verts = [(0.0, 0.0, 0.0),
                 (0.0, depth, 0.0),
                 (width, depth, 0.0),
                 (width, 0.0, 0.0),
                 ]
    
        faces = [(0, 1, 2, 3),
                ]
        
        mesh = bpy.data.meshes.new("Plane")
        
        bm = bmesh.new()
    
        for v_co in verts:
            bm.verts.new(v_co)
        
        for f_idx in faces:
            bm.verts.ensure_lookup_table()
            bm.faces.new([bm.verts[i] for i in f_idx])
        
        bm.to_mesh(mesh)
        
        mesh.update()
        
        obj_mesh = bpy.data.objects.new(mesh.name, mesh)

        context.scene.collection.objects.link(obj_mesh)     
        self.plane = obj_mesh

    def invoke(self, context, event):
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        # self._draw_handle = context.space_data.draw_handler_add(
        #     self.draw_opengl, (context,), 'WINDOW', 'POST_PIXEL')
        self.placed_first_point = False
        self.selected_point = (0,0,0)
        
        self.create_drawing_plane(context)
        
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}


class GetPositionOnGrid(bpy.types.Operator):
    """Get a 3D position on the grid based on mouse cursor position"""
    
    bl_idname = "nevil.get_position_on_grid"
    bl_label = "Get position on the grid"
    
    # This function is just for testing
    def create_test_empty(self, context):
        '''Create an empty, link it to the scene and show the axis'''
        
        if bpy.data.objects.get("TestEmpty"):
            bpy.data.objects.remove(bpy.data.objects["TestEmpty"], do_unlink = True)
            
        manipulator_empty = bpy.data.objects.new("TestEmpty", None)
        scene_collection = context.layer_collection.collection
        scene_collection.objects.link(manipulator_empty)
        manipulator_empty.show_axis = True
        
        return manipulator_empty  
    
    def invoke (self, context, event):
        
        viewport_region = context.region
        viewport_region_data = context.space_data.region_3d
        viewport_matrix = viewport_region_data.view_matrix.inverted()
        
        # Shooting a ray from the camera, through the mouse cursor towards the grid with a length of 100000
        # If the camera is more than 100000 units away from the grid it won't detect a point
        ray_start = viewport_matrix.to_translation()
        ray_depth = viewport_matrix @ Vector((0,0,-100000))
        
        # Get the 3D vector position of the mouse
        ray_end = view3d_utils.region_2d_to_location_3d(viewport_region,viewport_region_data, (event.mouse_region_x, event.mouse_region_y), ray_depth )
        
        # A triangle on the grid plane. We use these 3 points to define a plane on the grid
        point_1 = Vector((0,0,0))
        point_2 = Vector((0,1,0))
        point_3 = Vector((1,0,0))
        
        # Create a 3D position on the grid under the mouse cursor using the triangle as a grid plane
        # and the ray cast from the camera
        position_on_grid = mathutils.geometry.intersect_ray_tri(point_1,point_2,point_3,ray_end,ray_start,False )
        
        # Create an empty for testing
        empty = self.create_test_empty(context)
        # Place the empty on the grid under the mouse cursor
        empty.location = position_on_grid
        
        return {'FINISHED'}

classes = (
    GetPositionOnGrid,
    )

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()








classes = (
    BP_OT_draw_plane,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()