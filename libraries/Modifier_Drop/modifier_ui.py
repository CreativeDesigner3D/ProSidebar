import bpy

class Modifier_PT_library_settings(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Library"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 18

    def draw(self, context):
        layout = self.layout
        layout.operator("modifier.save_current_modifier_stack_to_library",icon='MODIFIER_ON')


class Modifier_OT_prompts(bpy.types.Operator):
    bl_idname = "modifier.prompts"
    bl_label = "Modifier Prompts"

    obj = None
    mod = None

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        self.obj = context.object
        self.get_modifier()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_modifier(self):
        for mod in self.obj.modifiers:
            self.mod = mod
            break

    def draw_arrary_modifier(self,layout):
        layout.prop(self.mod, "fit_type")

        if self.mod.fit_type == 'FIXED_COUNT':
            layout.prop(self.mod, "count")
        elif self.mod.fit_type == 'FIT_LENGTH':
            layout.prop(self.mod, "fit_length")
        elif self.mod.fit_type == 'FIT_CURVE':
            layout.prop(self.mod, "curve")

        layout.separator()

        split = layout.split()

        col = split.column()
        col.prop(self.mod, "use_constant_offset")
        sub = col.column()
        sub.active = self.mod.use_constant_offset
        sub.prop(self.mod, "constant_offset_displace", text="")

        col.separator()

        col.prop(self.mod, "use_merge_vertices", text="Merge")
        sub = col.column()
        sub.active = self.mod.use_merge_vertices
        sub.prop(self.mod, "use_merge_vertices_cap", text="First Last")
        sub.prop(self.mod, "merge_threshold", text="Distance")

        col = split.column()
        col.prop(self.mod, "use_relative_offset")
        sub = col.column()
        sub.active = self.mod.use_relative_offset
        sub.prop(self.mod, "relative_offset_displace", text="")

        col.separator()

        col.prop(self.mod, "use_object_offset")
        sub = col.column()
        sub.active = self.mod.use_object_offset
        sub.prop(self.mod, "offset_object", text="")

        row = layout.row()
        split = row.split()
        col = split.column()
        col.label(text="UVs:")
        sub = col.column(align=True)
        sub.prop(self.mod, "offset_u")
        sub.prop(self.mod, "offset_v")
        layout.separator()

        layout.prop(self.mod, "start_cap")
        layout.prop(self.mod, "end_cap")        

    def draw(self, context):
        layout = self.layout
        layout.label(text=self.obj.name)
        if self.mod.type == 'ARRAY':
            self.draw_arrary_modifier(layout)

bpy.utils.register_class(Modifier_PT_library_settings)
bpy.utils.register_class(Modifier_OT_prompts)        