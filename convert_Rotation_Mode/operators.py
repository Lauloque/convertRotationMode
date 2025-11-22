# SPDX-License-Identifier: GPL-3.0-or-later
from typing import Set
import bpy
from bpy.types import Operator
from bpy.types import Context
from .utils import (
    dprint,
    process_bone_conversion,
    store_initial_state,
    restore_initial_state,
    init_progress,
    finish_progress,
    is_any_pose_bone_selected,
)
from .bl_logger import logger


class CRM_OT_convert_rotation_mode(Operator):
    """Convert the selected pose bone's rotation mode."""
    bl_idname = "crm.convert_rotation_mode"
    bl_label = "Convert Rotation Mode"
    bl_description = "Convert the selected bone's rotation mode."
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context: Context) -> bool:
        """Filter for pose mode, selected bones, and CGT addon enabled"""
        addons = context.preferences.addons
        has_cgt_addon = addons.find("copy_global_transform") != -1
        is_pose_mode = context.mode == 'POSE'
        has_selected_bones = is_any_pose_bone_selected()

        return has_cgt_addon and is_pose_mode and has_selected_bones

    def execute(self, context: Context) -> Set[str]:
        """main execution - convert rotation modes for selected bones."""

        target_rmode = context.scene.CRM_Properties.targetRmode
        selected_bone_names = [
            bone.name for bone in context.selected_pose_bones
        ]
        bone_count = len(selected_bone_names)

        dprint(
            f"Starting conversion for {bone_count} bones: "
            f"{selected_bone_names}"
        )

        store_initial_state(context)
        init_progress(context, bone_count)

        # Process each bone by name
        for bone_name in selected_bone_names:
            if bone_name in context.object.pose.bones:
                current_bone = context.object.pose.bones[bone_name]
                process_bone_conversion(context, current_bone)
            else:
                dprint(f"Warning: Bone '{bone_name}' not found.")

        logger.info(" # No more bones to work on.")

        # Progress cleanup
        finish_progress(context)
        self.report(
            {"INFO"},
            f"Successfully converted {bone_count} bone(s) to "
            f"'{target_rmode}'"
        )

        restore_initial_state(context)

        return {'FINISHED'}
