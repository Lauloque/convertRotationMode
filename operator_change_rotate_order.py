import bpy
from bpy.props import (
    StringProperty,
)

def main(context):
    for ob in context.scene.objects:
        print(ob)


class Animation_OT_changeRotateOrder(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.change_rotate_order"
    bl_label = "change rotate order"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    activeBone = bpy.context.active_pose_bone
    targetRmode = "YXZ"

    currentRmode = activeBone.rotation_mode
#    print ("Current rotation mode for:")
#    print (str(activeBone))
#    print ("is: " + currentRmode)
#    print ( )
#    print ("New rotate order will be:")
#    print (targetRmode)
    
    if bpy.context.object.mode == 'POSE':

        listBones = bpy.context.selected_pose_bones
        
        for currentBone in listBones:
#            print(currentBone)
            bpy.ops.pose.select_all(action='DESELECT')
            currentBone.bone.select = True
            print(currentBone)
            print(currentBone.rotation_mode)

    def execute(self, context):
        main(context)
#        Check if pose or object mode
#        if bpy.context.object.mode == "POSE":
#            selectedObj = bpy.context.selected_pose_bones
#        else:
#            selectedObj = bpy.context.selected_objects


#        cycle through each selected object. Will need a refactor to
#        set current python object as active, as current global 
#        transform addon works only on active object.
#        
#        for object in selectedObj:
#            print (object.rotation_mode)
#            currentRmode = object.rotation_mode
#            print ("Current rotation mode for " + str(object) + " is: " + currentRmode)
#            object.rotation_mode = 'XYZ'
#            bpy.ops.object.copy_global_transform()
#            object.rotation_mode = 'YXZ'
#            bpy.ops.object.paste_transform(method='CURRENT')
        
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
