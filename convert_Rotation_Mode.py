bl_info = {
    "name": "Convert Rotation Mode",
    "author": "Loïc \"L0Lock\" Dautry",
    "version": (1, 0, 0),
    "blender": (3, 2, 1),
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

dev_mode = False
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

    def get_fcurves(self, obj):
        try:    return obj.animation_data.action.fcurves
        except: return None

    def get_keyed_frames(self, context, bone_name):
        
        ### GET ACTIVE OBJECT'S FCURVES LIST
        fcurves = self.get_fcurves(context.active_object)
        if fcurves == None:
            if dev_mode == True: ###### DEV OUTPUT
                print(f' # get_fcurves(): Anim Data not found on Armature.')
            keyed_frames_list = None
            return keyed_frames_list
            
        elif fcurves != None:
            if dev_mode == True: ###### DEV OUTPUT
                print(f' # get_fcurves(): Found Anim Data on Armature.')
                for curve in fcurves:
                    print(f' | # curve: {curve.data_path}')

        bone_filer_list = []
                
        for curve in fcurves:
            curve_path = curve.data_path.split('"')[1]
            
            ### EXTRACT CURRENT BONE'S FCURVES
            if dev_mode == True: ###### DEV OUTPUT
                print(f' # bone_filter_list[]: comparing paths \"{curve_path}\" with \"{bone_name}\"')   
                         
            if curve_path == bone_name:
                keyframePoints = curve.keyframe_points
                
                ### BUILD 
                bone_filer_list.append({
                    "bone_name": curve.data_path.split('"')[1],
                    "keyed_frames": [kp.co[0] for kp in keyframePoints],
                })
                
        if bone_filer_list == []: 
            if dev_mode == True: ###### DEV OUTPUT
                print(f' # bone_filter_list[]: Anim Data not found on Bone:  \"{bone_name}\""')
                print(f' |  # bone_filer_list[]   :\n |  | # {bone_filer_list}')
            keyed_frames_list = None
            return keyed_frames_list
        else:               
            if dev_mode == True: ###### DEV OUTPUT
                print(f' # bone_filter_list[]: Found Anim Data on Bone.')
            
            #### CLEANUP DUPLICATES
            keyed_frames_list = []
            for i in bone_filer_list:
                if i not in keyed_frames_list: 
                    keyed_frames_list.append(i)
                    if dev_mode == True: ###### DEV OUTPUT
                        print(f' # Built keyed_frames_list[] for \"{bone_name}:\"')
                        for bName in keyed_frames_list:
                            print(f' |  # Keyed Frames: {bName["keyed_frames"]}\n #')
            
        return keyed_frames_list

    def execute(self, context):
        scene = context.scene
        CRM_Properties = scene.CRM_Properties

        listBones = context.selected_pose_bones 
        
        for currentBone in listBones:
            bpy.ops.pose.select_all(action='DESELECT')
            context.object.data.bones.active = currentBone.bone
            currentBone.bone.select = True
            if dev_mode == True: ###### DEV OUTPUT
                print(f'### Working on bone \"{currentBone.bone.name}\" ###')
                print(f' # Target Rmode will be {CRM_Properties.targetRmode}')
            originalRmode = currentBone.rotation_mode
            ################################## START OF FRAME CYCLE
            keyed_frames_list = self.get_keyed_frames(context, currentBone.bone.name)
            if keyed_frames_list is None:
                self.report({"ERROR"}, "No animation found (ㆆ_ㆆ)")
                return {'CANCELLED'} 
            for bName in keyed_frames_list:
                if bName["bone_name"] == context.active_bone.name:
                    if dev_mode == True: ###### DEV OUTPUT
                        print(f' # Using keyed_frames_list of \"{bName["bone_name"]}\":')
                    for KdFrame in bName["keyed_frames"]:
                        context.scene.frame_current = int(KdFrame)
                        if dev_mode == True: ###### DEV OUTPUT
                            print(f' |  # Jumped to frame {int(KdFrame)}')

                        currentBone.rotation_mode = originalRmode
                        if dev_mode == True: ###### DEV OUTPUT
                            print(f' |  # \"{currentBone.name}\" Rmode set to original {originalRmode}')

                        bpy.ops.object.copy_global_transform()
                        if dev_mode == True: ###### DEV OUTPUT
                            print(f' |  # Copied \"{currentBone.name}\" Global Transform')

                        currentBone.rotation_mode = CRM_Properties.targetRmode
                        if dev_mode == True: ###### DEV OUTPUT
                            print(f' |  # Rmode set to {CRM_Properties.targetRmode}')

                        bpy.ops.object.paste_transform(method='CURRENT')
                        if dev_mode == True: ###### DEV OUTPUT
                            print(f' |  # Pasted \"{currentBone.name}\" Global Transform')
                            print(f' # Done working on ",currentBone.name,", moving to next one!\n # ')
                    break
        
        self.report({"INFO"}, "Successfully converted to " + CRM_Properties.targetRmode)



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

class VIEW3D_PT_Rmodes_recommandations(Panel):##################################################
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

def update_devMode(self, context):
    message = "Convert Rotation Mode: Toggling dev mode has failed"
    try:
        globals()['dev_mode'] = context.preferences.addons[__name__].preferences.devMode
        print('dev_mode toggled')

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

        row.prop(self, "category")
        row.prop(self, "devMode")

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