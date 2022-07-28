bl_info = {
    "name": "Convert Rotation Mode",
    "author": "Loïc \"L0Lock\" Dautry",
    "version": (0, 0, 4),
    "blender": (3, 1, 0),
    "location": "3D Viewport → Sidebar → Animation Tab",
    "category": "Animation",
    "warning": "Work in progress, use at your own risk!",
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

dev_mode = True
C = bpy.context

class ConvertRotaitonMode_Properties(PropertyGroup):
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

    # dev mode boolean
    # dev_mode: BoolProperty(
    #     name="Developer Mode",
    #     default= False)


class ConvertRotationOrderPanel:
##################################################
# Check if Pose mode, for drawing panel

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
##################################################
# Main Conversion Operator
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

    # def get_originalRmode(self, currentBone):
    #     self.report({"INFO"}, currentBone.name + " Rmode is " + currentBone.rotation_mode)
    #     originalRmode = currentBone.rotation_mode
    #     currentBone.rotation_mode = originalRmode

    #     return(originalRmode)

    def get_fcs(self, obj):
        try:    return obj.animation_data.action.fcurves
        except: return None

    def get_keyed_frames(self):
        fcs = self.get_fcs(C.object)

        if fcs is None:
            print("No animation_data / invalid object")
            return None

        ARRAY = []
        
        for fc in fcs:
            bone_name = fc.data_path
            index = fc.array_index

            ### EXTRACT BONES PATHS FROM FCURVES
            if bone_name[: 10] != "pose.bones": continue
            ### EXTRACT BONE NAMES FROM BONES PATHS
            try:
                bone_name = re.search('pose.bones\["(.+?)\"].', bone_name).group(1)
            except AttributeError:
                bone_name = "search failed!"
            ### BUILD 
            ARRAY.append({
                "bone_name": bone_name,
                "keyed_frames": [kp.co[0] for kp in fc.keyframe_points]
            })
            
            #### CLEANUP DUPLICATES
            keyed_frames_list = [] 
            for i in ARRAY: 
                if i not in keyed_frames_list: 
                    keyed_frames_list.append(i) 
            
        if ARRAY is None and dev_mode == True:
            print("Failed to get list of Bones")

        return keyed_frames_list

    def execute(self, context):
        scene = context.scene
        CRM_Properties = scene.CRM_Properties

        listBones = C.selected_pose_bones
        keyed_frames_list = self.get_keyed_frames()
        
        for currentBone in listBones:
            bpy.ops.pose.select_all(action='DESELECT')
            C.object.data.bones.active = currentBone.bone
            currentBone.bone.select = True
            if dev_mode == True: ###### DEV OUTPUT
                print("### Working on bone ", currentBone.name, " ###")
                print("Target Rmode will be", CRM_Properties.targetRmode)
            originalRmode = currentBone.rotation_mode
            ################################## START OF FRAME CYCLE
            for bName in keyed_frames_list:
                if bName["bone_name"] == C.active_bone.name:
                    print("########  Using keyed_frames_list of",bName["bone_name"],"  ########")
                    for KdFrame in bName["keyed_frames"]:
                        C.scene.frame_current = int(KdFrame)
                        if dev_mode == True: ###### DEV OUTPUT
                            print('jumped to frame ', int(KdFrame))

                        currentBone.rotation_mode = originalRmode
                        if dev_mode == True: ###### DEV OUTPUT
                            print(currentBone.name, " Rmode set to original ", originalRmode)

                        bpy.ops.object.copy_global_transform()
                        if dev_mode == True: ###### DEV OUTPUT
                            print("Copied ", currentBone.name, " Global Transform")

                        currentBone.rotation_mode = CRM_Properties.targetRmode
                        if dev_mode == True: ###### DEV OUTPUT
                            print("Rmode set to ", CRM_Properties.targetRmode)

                        bpy.ops.object.paste_transform(method='CURRENT')
                        if dev_mode == True: ###### DEV OUTPUT
                            print("Pasted ", currentBone.name, " Global Transform")
                            print("Done working on ", currentBone.name, " moving to next one! \n \n")
                    break
                else:
                    if dev_mode == True:###### DEV OUTPUT
                        print("List for ", bName["bone_name"], " doesn't match bone ", C.active_bone.name)
        
        self.report({"INFO"}, "Successfully converted to " + CRM_Properties.targetRmode)



        return{'FINISHED'}

# remove following 'ConvertRotationOrderPanel' once addon functional outside pose mode.
class VIEW3D_PT_convert_rotation_mode(ConvertRotationOrderPanel, Panel):
##################################################
# Sidebar UI

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
        # autokey_row = col.layout.column(align=True)
        # autokey_row.enabled = has_autokey

        col.label(text="Target Rotation Mode")                                        
        col.prop(CRM_Properties, "targetRmode", text="")

        if not has_autokey:
            col.label(text="Please turn on Auto-Keying!", icon="ERROR")
        col.operator("object.convert_rotation_mode", text="Convert!")


##################################################
# Addon's preferences

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

class CRM_OT_enableAddon(bpy.types.Operator):
    bl_idname = 'crm.enable_addon'
    bl_label = "Enable \"Copy Gloabl Transform\""
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self,context):
        bpy.ops.preferences.addon_enable(module="copy_global_transform")
        return{'FINISHED'}

class AddonPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__
    # CRM_Properties = C.scene.CRM_Properties

    # dev_mode: BoolProperty(name="Developer Mode",default= False)

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
        # col.label(text="Tab Category:")
        col.prop(self, "category")
        # col.prop(CRM_Properties, "dev_mode")

        if C.preferences.addons.find("copy_global_transform") == -1:
            col.label(text="This addon requires the addon \"Copy Gloabl Transform\" by Sybren A. Stüvel.", icon="ERROR")
            col.operator("crm.enable_addon")


classes = (
    ConvertRotaitonMode_Properties,
    OBJECT_OT_convert_rotation_mode,
    VIEW3D_PT_convert_rotation_mode,
    AddonPreferences,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.CRM_Properties = bpy.props.PointerProperty(type=ConvertRotaitonMode_Properties)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.CRM_Properties