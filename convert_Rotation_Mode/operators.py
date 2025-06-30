# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
from bpy.types import Operator
from bpy.types import Context
from .utils import (
    dprint,
    is_pose_mode,
    get_fcurves,
    get_rotation_locks,
    toggle_rotation_locks,
    jump_next_frame,
)


class CRM_OT_convert_rotation_mode(Operator):
    """Convert the selected pose bone's rotation mode."""
    bl_idname = "crm.convert_rotation_mode"
    bl_label = "Convert Rotation Mode"
    bl_description = "Convert the selected bone's rotation mode."
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        """Filter"pose mode and CGT addon enabled"""
        addons = context.preferences.addons
        mode = context.mode
        if addons.find("copy_global_transform") != -1 and mode == 'POSE':
            return len(context.selected_pose_bones) > 0
        return False > 0

    def execute(self, context):
        """main execution"""
        scene = context.scene
        CRM_Properties = scene.CRM_Properties
        wm = bpy.context.window_manager

        has_autokey = scene.tool_settings.use_keyframe_insert_auto
        scene.tool_settings.use_keyframe_insert_auto = True

        initial_active_bone = context.object.data.bones.active
        selected_bones = context.selected_pose_bones
        start_frame = context.scene.frame_start
        end_frame = context.scene.frame_end
        initial_frame = context.scene.frame_current
        duration = end_frame - start_frame
        amount = len(selected_bones)

        progress_max = amount * duration
        wm.progress_begin(0, progress_max)

        for current_bone in selected_bones:

            bpy.ops.pose.select_all(action='DESELECT')
            context.object.data.bones.active = current_bone.bone
            current_bone.bone.select = True
            dprint(
                f"### Working on bone '{current_bone.bone.name}' ###"
            )
            dprint(
                f" # Target Rmode will be {CRM_Properties.targetRmode}"
            )

            locks = get_rotation_locks(current_bone)
            toggle_rotation_locks(current_bone, 'OFF')
            dprint(" |  # Backed up and unlocked rotations")

            original_rmode = current_bone.rotation_mode
            bpy.ops.screen.frame_jump(end=False)
            current_bone.rotation_mode = original_rmode
            current_bone.keyframe_insert(
                "rotation_mode",
                frame=1,
                group=current_bone.name
            )
            cnt = 1

            while context.scene.frame_current <= end_frame:
                current_frame = context.scene.frame_current
                dprint(f" |  # Jumped to frame {current_frame}")
                progress_current = cnt * current_frame
                wm.progress_update(progress_current)

                current_bone.rotation_mode = original_rmode
                current_bone.keyframe_insert(
                    "rotation_mode",
                    frame=current_frame,
                    group=current_bone.name
                )
                dprint(
                    f" |  |  # '{current_bone.name}' Rmode set to "
                    f"{current_bone.rotation_mode}"
                )

                bpy.ops.object.copy_global_transform()
                dprint(
                    f" |  |  # Copied '{current_bone.name}' Global "
                    f"Transform as {original_rmode}"
                )

                current_bone.rotation_mode = CRM_Properties.targetRmode
                current_bone.keyframe_insert(
                    "rotation_mode",
                    frame=current_frame,
                    group=current_bone.name)
                dprint(
                    f" |  |  # Rmode set to {current_bone.rotation_mode}"
                )

                bpy.ops.object.paste_transform(
                    method='CURRENT',
                    use_mirror=False
                )
                dprint(
                    f" |  |  # Pasted '{current_bone.name}' Global Transform "
                    f"as {current_bone.rotation_mode}"
                )
                for path in (
                    "rotation_axis_angle",
                    "rotation_euler",
                    "rotation_mode",
                    "rotation_quaternion",
                ):
                    current_bone.keyframe_insert(data_path=path)
                dprint(
                    f" |  |  # Keyframed '{current_bone.name}' rotations"
                )

                jump_next_frame(context)
                if current_frame == context.scene.frame_current:
                    break

            if CRM_Properties.preserveLocks:
                toggle_rotation_locks(current_bone, 'ON', locks)
                dprint(" |  # Reverted rotation locks")

            dprint(
                f" # No more keyframes on '{current_bone.name}'.#"
            )
        dprint(" # No more bones to work on.")

        wm.progress_end()
        self.report(
            {"INFO"},
            f"Successfully converted {len(selected_bones)} bone(s) to "
            f"'{CRM_Properties.targetRmode}'"
        )

        if CRM_Properties.jumpInitFrame:
            context.scene.frame_current = initial_frame
        if CRM_Properties.preserveSelection:
            for bone in selected_bones:
                bone.bone.select = True
            context.object.data.bones.active = initial_active_bone

        scene.tool_settings.use_keyframe_insert_auto = has_autokey
        return {'FINISHED'}
