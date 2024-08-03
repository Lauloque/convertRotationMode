# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
from bpy.types import Operator
from bpy.types import Context
from .utils import devOut, is_pose_mode, get_fcurves, toggle_rotation_locks, jump_next_frame

class CRM_OT_convert_rotation_mode(Operator):
    bl_idname = "crm.convert_rotation_mode"
    bl_label = "Convert Rotation Mode"
    bl_description = "Convert the selected bone's rotation order on all keyframes."
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.preferences.addons.find("copy_global_transform") != -1 and len(context.selected_pose_bones) > 0


    def execute(self, context):
        scene = context.scene
        CRM_Properties = scene.CRM_Properties
        wm = bpy.context.window_manager

        has_autokey = scene.tool_settings.use_keyframe_insert_auto
        scene.tool_settings.use_keyframe_insert_auto = True

        initActive = context.object.data.bones.active
        listBones = context.selected_pose_bones
        startFrame = context.scene.frame_start
        endFrame = context.scene.frame_end
        initFrame = context.scene.frame_current
        duration = endFrame - startFrame
        amount = len(listBones)

        progressMax = amount * duration
        wm.progress_begin(0, progressMax)

        devOut(context, '##################\n### test message devMode\n############')
        devOut(context, f'# i like my {endFrame}')

        for currentBone in listBones:

            bpy.ops.pose.select_all(action='DESELECT')
            context.object.data.bones.active = currentBone.bone
            currentBone.bone.select = True
            devOut(context, f'### Working on bone \"{currentBone.bone.name}\" ###')
            devOut(context, f' # Target Rmode will be {CRM_Properties.targetRmode}')

            self.locks = []
            self.locks.append(currentBone.lock_rotation[0])
            self.locks.append(currentBone.lock_rotation[1])
            self.locks.append(currentBone.lock_rotation[2])
            self.locks.append(currentBone.lock_rotation_w)
            self.locks.append(currentBone.lock_rotations_4d)
            toggle_rotation_locks('OFF', currentBone)
            devOut(context, f' |  # Backed up and unlocked rotations')

            originalRmode = currentBone.rotation_mode
            bpy.ops.screen.frame_jump(end=False)
            currentBone.rotation_mode = originalRmode
            currentBone.keyframe_insert("rotation_mode", frame=1, group=currentBone.name)
            cnt = 1

            while context.scene.frame_current <= endFrame:
                curFrame = context.scene.frame_current
                devOut(context, f' |  # Jumped to frame {curFrame}')
                progressCurrent = cnt * curFrame
                wm.progress_update(progressCurrent)

                currentBone.rotation_mode = originalRmode
                currentBone.keyframe_insert("rotation_mode", frame=curFrame, group=currentBone.name)
                devOut(context, f' |  |  # \"{currentBone.name}\" Rmode set to {currentBone.rotation_mode}')

                bpy.ops.object.copy_global_transform()
                devOut(context, f' |  |  # Copied \"{currentBone.name}\" Global Transform as {originalRmode}')

                currentBone.rotation_mode = CRM_Properties.targetRmode
                currentBone.keyframe_insert("rotation_mode", frame=curFrame, group=currentBone.name)
                devOut(context, f' |  |  # Rmode set to {currentBone.rotation_mode}')

                bpy.ops.object.paste_transform(method='CURRENT', use_mirror=False)
                devOut(context, f' |  |  # Pasted \"{currentBone.name}\" Global Transform as {currentBone.rotation_mode}')

                jump_next_frame(context)
                if curFrame == context.scene.frame_current:
                    break

            if CRM_Properties.preserveLocks:
                toggle_rotation_locks('ON', currentBone)
                devOut(context, f' |  # Reverted rotation locks')

            devOut(context, f' # No more keyframes on "{currentBone.name}", moving to next bone.\n # ')
        devOut(context, f' # No more bones to work on.')

        wm.progress_end()
        self.report({"INFO"}, f"Successfully converted {len(listBones)} bone(s) to '{CRM_Properties.targetRmode}'")

        if CRM_Properties.jumpInitFrame:
            context.scene.frame_current = initFrame
        if CRM_Properties.preserveSelection:
               for bone in listBones:
                   bone.bone.select = True
               context.object.data.bones.active = initActive

        scene.tool_settings.use_keyframe_insert_auto = has_autokey
        return {'FINISHED'}
