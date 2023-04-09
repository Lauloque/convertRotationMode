bl_info = {
    "name": "Convert Rotation Mode",
    "author": "Loïc \"L0Lock\" Dautry",
    "version": (1, 2, 2),
    "blender": (3, 5, 0),
    "location": "3D Viewport → Sidebar → Animation Tab",
    "category": "Animation",
    "warning": "Requires the addon \"Copy Gloabl Transform\" available since Blender v3.1",
    "support": 'COMMUNITY',
    "doc_url": "https://github.com/L0Lock/convertRotationMode",
    "tracker_url": "https://github.com/L0Lock/convertRotationMode/issues",
}

import bpy, re
from bpy.props import (
    StringProperty, EnumProperty, BoolProperty,
)
from bpy.types import (
    Context,  Object,
    Operator, Panel,
    PoseBone, PropertyGroup,
    AddonPreferences, 
    )

C = bpy.context

class CRM_Props(PropertyGroup):
##################################################
    
    # Lists all rotation modes for the UI
    targetRmode: EnumProperty(
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


class CRM_UI_PoseModeChecker:
##################################################
# Check if Pose mode, for drawing panel

    @classmethod
    def crm_panel_poll(cls, context: Context) -> bool:
        return bool(
            context.object
            and context.object.mode == 'POSE'
        )

    @classmethod
    def poll(cls, context: Context) -> bool:
        return cls.crm_panel_poll(context);

class CRM_OT_convert_rotation_mode(Operator):
##################################################
# Main Conversion Operator
    bl_idname = "crm.convert_rotation_mode"
    bl_label = "Convert Rotation Mode"
    bl_description = "Convert the selected bone's rotation order on all keyframes."
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_pose_bones
    
    def devOut(self, context, msg):
        if context.preferences.addons[__name__].preferences.devMode == True:
            print(msg)

    def get_fcurves(self, obj):
        try:    return obj.animation_data.action.fcurves
        except: return None

    def lockSwitch(self, mode, currentBone):
        if mode == 'OFF':
            currentBone.lock_rotation[0] = False
            currentBone.lock_rotation[1] = False
            currentBone.lock_rotation[2] = False
            currentBone.lock_rotation_w = False
            currentBone.lock_rotations_4d = False
        if mode == 'ON':
            currentBone.lock_rotation[0] = self.locks[0]
            currentBone.lock_rotation[1] = self.locks[1]
            currentBone.lock_rotation[2] = self.locks[2]
            currentBone.lock_rotation_w = self.locks[3]
            currentBone.lock_rotations_4d = self.locks[4]

    def jumpNext(self, context):
        bpy.ops.screen.keyframe_jump(next=True)
        context.scene.frame_current += 1
        context.scene.frame_current -= 1

    def execute(self, context):
        scene = context.scene
        CRM_Properties = scene.CRM_Properties

        listBones = context.selected_pose_bones
        startFrame = context.scene.frame_start
        endFrame = context.scene.frame_end
        initFrame = context.scene.frame_current

        self.devOut(context, '##################\n### test message devMode\n############')
        self.devOut(context, f'# i like my {endFrame}')

        for currentBone in listBones:

            ### Updating bone selection
            bpy.ops.pose.select_all(action='DESELECT')
            context.object.data.bones.active = currentBone.bone
            currentBone.bone.select = True
            self.devOut(context, f'### Working on bone \"{currentBone.bone.name}\" ###')
            self.devOut(context, f' # Target Rmode will be {CRM_Properties.targetRmode}')

            ### Check lock states
            self.locks = []
            self.locks.append(currentBone.lock_rotation[0])
            self.locks.append(currentBone.lock_rotation[1])
            self.locks.append(currentBone.lock_rotation[2])
            self.locks.append(currentBone.lock_rotation_w)
            self.locks.append(currentBone.lock_rotations_4d)
            self.lockSwitch('OFF', currentBone)
            self.devOut(context, f' |  # Backed up and unlocked rotations')

            originalRmode = currentBone.rotation_mode
            bpy.ops.screen.frame_jump(end=False)
            currentBone.keyframe_insert("rotation_mode", frame=1)

            while context.scene.frame_current <= endFrame:

                curFrame = context.scene.frame_current
                self.devOut(context, f' |  # Jumped to frame {curFrame}')

                currentBone.rotation_mode = originalRmode
                bpy.ops.anim.keyframe_insert_by_name(type="Available")
                self.devOut(context, f' |  |  # \"{currentBone.name}\" Rmode set to original {currentBone.rotation_mode}')

                bpy.ops.object.copy_global_transform()
                self.devOut(context, f' |  |  # Copied \"{currentBone.name}\" Global Transform')

                currentBone.rotation_mode = CRM_Properties.targetRmode
                currentBone.keyframe_insert("rotation_mode", frame=curFrame)
                self.devOut(context, f' |  |  # Rmnode set to {currentBone.rotation_mode}')

                bpy.ops.object.paste_transform(method='CURRENT')
                self.devOut(context, f' |  |  # Pasted \"{currentBone.name}\" Global Transform')

                self.jumpNext(context)
                if curFrame == context.scene.frame_current:
                    break
            
            ### Reverting lock states
            if context.preferences.addons[__name__].preferences.preserveLocks == True:
                self.lockSwitch('ON', currentBone)
                self.devOut(context, f' |  # Reverted rotation locks')

            self.devOut(context, f' # No more keyframes on "{currentBone.name}", moving to next bone.\n # ')
        self.devOut(context, f' # No more bones to work on.')

        self.report({"INFO"}, f"Successfully converted {len(listBones)} bone(s) to '{CRM_Properties.targetRmode}'")
        
        if context.preferences.addons[__name__].preferences.jumpInitFrame == True:
            context.scene.frame_current = initFrame

        return{'FINISHED'}

# remove following 'CRM_UI_PoseModeChecker' once addon functional outside pose mode.
class VIEW3D_PT_convert_rotation_mode(CRM_UI_PoseModeChecker, Panel):
##################################################
# Sidebar Main UI

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Animation"
    bl_label = "Convert Rotation Mode"

    def draw(self, context: Context) -> None:
        layout = self.layout

        obj = context.object
        scene = context.scene
        CRM_Properties = scene.CRM_Properties

        has_autokey = scene.tool_settings.use_keyframe_insert_auto

        col = layout.column(align=True)

        col.label(text="Target Rotation Mode")                                        
        col.prop(CRM_Properties, "targetRmode", text="")

        if not has_autokey:
            col.label(text="Please turn on Auto-Keying!", icon="ERROR")
        col.operator("crm.convert_rotation_mode", text="Convert!")

class VIEW3D_PT_Rmodes_recommandations(Panel):
##################################################
# Rmodes recommandations subpanel
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Animation"
    bl_parent_id = "VIEW3D_PT_convert_rotation_mode"
    bl_label = "Rotation Modes Cheat Sheet"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        grid = layout.grid_flow(columns=3, align=True, even_columns=True)
        grid.label(text="")
        grid.label(text="COG")
        grid.label(text="Hip")
        grid.label(text="Leg")
        grid.label(text="Shoulders")
        grid.label(text="Arm Upper")
        grid.label(text="Arm Lower")
        grid.label(text="Wrist")
        grid.label(text="Fingers")
        grid.label(text="Spine Base")
        grid.label(text="Spine Mid")
        grid.label(text="Chest")
        grid.label(text="Neck")
        grid.label(text="Head")
        grid.label(text="# Y Down (Blender)")
        grid.label(text="ZXY")
        grid.label(text="YZX")
        grid.label(text="ZXY")
        grid.label(text="YZX")
        grid.label(text="YXZ")
        grid.label(text="ZYX (or YZX)")
        grid.label(text="ZYX (or YZX)")
        grid.label(text="YZX")
        grid.label(text="ZXY")
        grid.label(text="YZX")
        grid.label(text="ZXY")
        grid.label(text="YXZ")
        grid.label(text="YXZ")
        grid.label(text="# X Down (not Blender)")
        grid.label(text="ZXY")
        grid.label(text="ZXY")
        grid.label(text="XZY")
        grid.label(text="XYZ")
        grid.label(text="ZXY")
        grid.label(text="ZXY")
        grid.label(text="XYZ (or YZX)")
        grid.label(text="YZX")
        grid.label(text="ZXY")
        grid.label(text="XZY")
        grid.label(text="ZXY")
        grid.label(text="YXZ")
        grid.label(text="YXZ")


##################################################
# Addon's preferences

# Define Panel classes for updating
panels = (
        VIEW3D_PT_convert_rotation_mode,
        VIEW3D_PT_Rmodes_recommandations,
        )

def update_panel(self, context):
    message = "Convert Rotation Mode: Updating Panel locations has failed"
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

class CRM_OT_enableAddon(Operator):
    bl_idname = 'crm.enable_addon'
    bl_label = "Enable \"Copy Gloabl Transform\""
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self,context):
        bpy.ops.preferences.addon_enable(module="copy_global_transform")
        return{'FINISHED'}

class AddonPreferences(AddonPreferences, Panel):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    devMode: BoolProperty(
        name="Developer Mode",
        description='Enables all error tracking messages.',
        default= False,
        update=update_devMode
        )
    
    jumpInitFrame: BoolProperty(
        name="Jump to initial frame",
        description='When done converting, jump back to the initial frame.',
        default= True
    )

    preserveLocks: BoolProperty(
        name="Preserve Locks",
        description="Preserves lock states on rotation channels.",
        default= True
    )

    category: StringProperty(
            name="Tab Category",
            description="Choose a name for the category of the panel (default: Animation).",
            default="Animation",
            update=update_panel
            )

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, "category")
        row.label(text="")
        row.prop(self, "devMode")
        row.prop(self, "jumpInitFrame")
        row.prop(self, "preserveLocks")

        row = layout.row()
        if context.preferences.addons.find("copy_global_transform") == -1:
            row.label(text="This addon requires the addon \"Copy Gloabl Transform\" by Sybren A. Stüvel.", icon="ERROR")
            row.operator("crm.enable_addon")

classes = (
    CRM_Props,
    CRM_OT_convert_rotation_mode,
    CRM_OT_enableAddon,
    VIEW3D_PT_convert_rotation_mode,
    VIEW3D_PT_Rmodes_recommandations,
    AddonPreferences,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.CRM_Properties = bpy.props.PointerProperty(type=CRM_Props)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.CRM_Properties