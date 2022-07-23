import bpy


def main(context):
    for ob in context.scene.objects:
        print(ob)


class Animation_OT_changeRotateOrder(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.change_rotate_order"
    bl_label = "change rotate order"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(context)
        bpy.context.active_pose_bone.rotation_mode = 'XYZ'
        bpy.ops.object.copy_global_transform()
        bpy.context.active_pose_bone.rotation_mode = 'YXZ'
        bpy.ops.object.paste_transform(method='CURRENT')
        
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(Animation_OT_changeRotateOrder.bl_idname, text=Animation_OT_changeRotateOrder.bl_label)


# Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access).
def register():
    bpy.utils.register_class(Animation_OT_changeRotateOrder)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(Animation_OT_changeRotateOrder)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.change_rotate_order()
