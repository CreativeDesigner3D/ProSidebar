def get_room_scene_props(context):
    return context.scene.room

def get_room_bp(obj):
    if "IS_ROOM_BP" in obj:
        return obj
    elif obj.parent:
        return get_room_bp(obj.parent)
