from .bp_lib import bp_types, bp_unit, bp_utils

class Part(bp_types.Assembly):
    category_name = "Parts"

class Wall(bp_types.Assembly):
    category_name = "Walls"

class Room(bp_types.Assembly):
    category_name = "Rooms"

class Window(bp_types.Assembly):
    category_name = "Windows"    

class Door(bp_types.Assembly):
    category_name = "Doors"    