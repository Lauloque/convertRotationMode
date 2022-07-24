bl_info = {
    "name": "Convert Rotation Mode",
    "author": "Loïc \"L0Lock\" Dautry",
    "version": (0, 0, 1),
    "blender": (3, 1, 0),
    "location": "3D Viewport → Sidebar → Animation Tab",
    "category": "Animation",
    "warning": "Work in progress, use at your own risk!",
    "support": 'COMMUNITY',
    "doc_url": "https://github.com/L0Lock/convertRotationMode",
    "tracker_url": "https://github.com/L0Lock/convertRotationMode/issues",
}

import bpy
from bpy.props import (
    StringProperty, EnumProperty,
)
from bpy.types import (
    Context,  Object,
    Operator, Panel,
    PoseBone, PropertyGroup,
    AddonPreferences, 
    )

class RmodesProperties(PropertyGroup):

    targetRmode: bpy.props.EnumProperty(
        name='Target Rotation Mode',
        description='Target Rotation Mode for the convertion.',
        items=[
            ("XYZ", "XYZ Euler", "XYZ Euler - Rotation Order - prone to Gimbal Lock (default)."),
            ("XZY", "XZY Euler", "XZY Euler - Rotation Order - prone to Gimbal Lock."),
            ("YXZ", "YXZ Euler", "YXZ Euler - Rotation Order - prone to Gimbal Lock."),
            ("YZX", "YZX Euler", "YZX Euler - Rotation Order - prone to Gimbal Lock."),
            ("ZXY", "ZXY Euler", "ZXY Euler - Rotation Order - prone to Gimbal Lock."),
            ("ZYX", "ZYX Euler", "ZYX Euler - Rotation Order - prone to Gimbal Lock."),
            ("AXIS_ANGLE", "Axis Angle (WXYZ)", "Axis Angle (WXYZ) – Defines a rotation around some axis defined by 3D-Vector."),
            ("QUATERNION", "Quaternion (WXYZ)", "Quaternion (WXYZ) – No Gimbal Lock but awful for animators in Graph Editor."),
            ],
        default='XYZ'
        ) 

"""
##################################################
Check if Pose mode, for drawing panel
##################################################
"""

class ConvertRotationOrderPanel:
    @classmethod
    def convert_rotation_mode_panel_poll(cls, context: Context) -> bool:
        return bool(
            context.object
            and context.object.mode == 'POSE'
        )

    @classmethod
    def poll(cls, context: Context) -> bool:
        return cls.convert_rotation_mode_panel_poll(context);

class OBJECT_OT_convert_rotation_mode(Operator):
    bl_idname = "object.convert_rotation_mode"
    bl_label = "Convert Rotation Mode"
    bl_description = "Convert the selected bone's rotation order on all keyframes."
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: Context) -> bool:
        if not context.object.mode == 'POSE':
            cls.poll_message_set("Requires to be in Pose Mode")
            self.report({"WARNING"}, "Requires to be in Pose Mode")
            return False
        if not context.active_pose_bone:
            cls.poll_message_set("Select a bone in Pose Mode")
            self.report({"WARNING"}, "Select a bone in Pose Mode")
            return False
        return True


    def execute(self, context):
        scene = context.scene
        myTool = scene.myTool
        self.report({"INFO"}, "Target Rmode will be " + myTool.targetRmode)

        if bpy.context.object.mode == 'POSE':

            listBones = bpy.context.selected_pose_bones
            
            for currentBone in listBones:
                bpy.ops.pose.select_all(action='DESELECT')
                currentBone.bone.select = True
                print(currentBone)
                self.report({"INFO"}, currentBone.name + " Rmode is " + currentBone.rotation_mode)
                print(currentBone.rotation_mode)

        return{'FINISHED'}

    # def get_currentRmode(self, context):
    #     if bpy.context.object.mode == 'POSE':

    #         listBones = bpy.context.selected_pose_bones
            
    #         for currentBone in listBones:
    #             bpy.ops.pose.select_all(action='DESELECT')
    #             currentBone.bone.select = True
    #             self.report({"INFO"}, 
    #                 currentBone + " Rmode is " + currentBone.rotation_mode)
    #     return{'FINISHED'}

#####################################################################
#                      SIDEBAR PANEL UI
#####################################################################

# remove following 'ConvertRotationOrderPanel' once addon functional outside pose mode.
class VIEW3D_PT_convert_rotation_mode(ConvertRotationOrderPanel, Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Animation"
    bl_label = "Convert Rotation Mode"

    def draw(self, context: Context) -> None:
        layout = self.layout

        obj = context.object
        scene = context.scene
        myTool = scene.myTool

        row = layout.row()
        row.label(text="Target Rotation Mode")

        row = layout.row()                                             
        row.prop(myTool, "targetRmode", text="")

        row = layout.row()
        row.operator("object.convert_rotation_mode", text="Convert!")

#####################################################################
#                      ADDON PREFERENCES
#####################################################################
# Define Panel classes for updating
panels = (
        VIEW3D_PT_convert_rotation_mode,
        )


def update_panel(self, context):
    message = "Align Tools: Updating Panel locations has failed"
    try:
        for panel in panels:
            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)

        for panel in panels:
            panel.bl_category = context.preferences.addons[__name__].preferences.category
            bpy.utils.register_class(panel)

    except Exception as e:
        print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
        pass


class AddonPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    category: StringProperty(
            name="Tab Category",
            description="Choose a name for the category of the panel (default: Animation).",
            default="Animation",
            update=update_panel
            )

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        col = row.column()
        col.label(text="Tab Category:")
        col.prop(self, "category", text="")


classes = (
    RmodesProperties,
    OBJECT_OT_convert_rotation_mode,
    VIEW3D_PT_convert_rotation_mode,
    AddonPreferences,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.myTool = bpy.props.PointerProperty(type=RmodesProperties)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.myTool