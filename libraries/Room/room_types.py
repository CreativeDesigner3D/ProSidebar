from .bp_lib import bp_types, bp_unit, bp_utils

class Part(bp_types.Assembly):
    category_name = "Parts"
    prompt_id = "room.part_prompts"

class Wall(bp_types.Assembly):
    category_name = "Walls"
    prompt_id = "room.wall_prompts"
    placement_id = "room.draw_multiple_walls"

class Room(bp_types.Assembly):
    category_name = "Rooms"
    menu_id = ""
    prompt_id = "room.room_prompts"
    placement_id = "room.place_square_room"

class Window(bp_types.Assembly):
    category_name = "Windows"

class Door(bp_types.Assembly):
    category_name = "Doors"
    placement_id = "room.place_door"