def get_assembly_bp(obj):
    if "IS_ASSEMBLY_BP" in obj:
        return obj
    elif obj.parent:
        return get_assembly_bp(obj.parent)