# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
from .ui import panels


def dprint(message: str):
    """Prints in the system console if the addon's developer printing is ON"""
    prefs = bpy.context.preferences.addons[__package__].preferences
    if prefs.developer_print:
        print(f"[Convert Rot Mode]: {message}")


def get_fcurves(obj):
    """Retrieve the F-Curves of an object."""
    try:
        return obj.animation_data.action.fcurves
    except AttributeError:
        return None


def jump_next_frame(context):
    """Jump to the next frame in the timeline."""
    bpy.ops.screen.keyframe_jump(next=True)
    context.scene.frame_current += 1
    context.scene.frame_current -= 1


def is_pose_mode(context):
    """Check if the active object is in Pose Mode."""
    return context.object and context.object.mode == 'POSE'


def toggle_rotation_locks(bone, mode, locks=None):
    """Toggle the rotation locks of a bone."""
    if mode == 'OFF':
        bone.lock_rotation[0] = False
        bone.lock_rotation[1] = False
        bone.lock_rotation[2] = False
        bone.lock_rotation_w = False
        bone.lock_rotations_4d = False
    elif mode == 'ON' and locks:
        bone.lock_rotation[0] = locks[0]
        bone.lock_rotation[1] = locks[1]
        bone.lock_rotation[2] = locks[2]
        bone.lock_rotation_w = locks[3]
        bone.lock_rotations_4d = locks[4]


def update_panel(self, context):
    """Update tab in which to place the panel"""
    try:
        # Ensure 'panels' is defined or imported
        from .ui import panels  # Import panels from the appropriate module

        for panel in panels:
            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)

        for panel in panels:
            addon = context.preferences.addons[__package__]
            panel.bl_category = addon.preferences.category
            bpy.utils.register_class(panel)

    except Exception as e:
        message = "Updating Panel locations has failed"
        dprint("\n[{}]\n{}\n\nError:\n{}".format(__package__, message, e))
