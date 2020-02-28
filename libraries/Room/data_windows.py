import bpy
import math
from .bp_lib import bp_types, bp_unit, bp_utils
import time
from . import room_types, room_utils

class Window(room_types.Part):
    show_in_library = True

    def draw(self):
        start_time = time.time()
        self.create_assembly("Window")