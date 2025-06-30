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
)


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
        has_selected_bones = len(context.selected_pose_bones) > 0

        return has_cgt_addon and is_pose_mode and has_selected_bones

    def execute(self, context: Context) -> Set[str]:
        """main execution - convert rotation modes for selected bones."""

        target_rmode = context.scene.CRM_Properties.targetRmode
        selected_bones = list(context.selected_pose_bones)

        store_initial_state(context)
        init_progress(context, len(selected_bones))

        # Process each bone
        for current_bone in selected_bones:
            process_bone_conversion(context, current_bone)

        dprint(" # No more bones to work on.")

        # Progress cleanup
        finish_progress(context)
        self.report(
            {"INFO"},
            f"Successfully converted {len(selected_bones)} bone(s) to "
            f"'{target_rmode}'"
        )

        restore_initial_state(context)

        return {'FINISHED'}
