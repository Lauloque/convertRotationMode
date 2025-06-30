# SPDX-License-Identifier: GPL-3.0-or-later
from typing import List, Optional, Union
import bpy
from bpy.types import Context, PoseBone, Bone
from .ui import panels

_progress_counter = 0


def dprint(message: str) -> None:
    """Prints in the system console if the addon's developer printing is ON"""
    prefs = bpy.context.preferences.addons[__package__].preferences
    if prefs.developer_print:
        print(f"[Convert Rot Mode]: {message}")


def get_fcurves(obj):
    """Retrieve the F-Curves of an object."""
    # Possibly obsolete
    try:
        return obj.animation_data.action.fcurves
    except AttributeError:
        return None


def get_rotation_locks(bone: PoseBone) -> List[bool]:
    """Return the current rotation lock state of the bone as a list."""
    return list(bone.lock_rotation) + [
        bone.lock_rotation_w,
        bone.lock_rotations_4d,
    ]


def jump_next_frame(context: Context) -> None:
    """
    Jump to the next frame in the timeline.
    Also jumps back and forth to force refresh the values for
    'Copy Global Transforms' to work properly when copying.
    """
    bpy.ops.screen.keyframe_jump(next=True)
    context.scene.frame_current += 1
    context.scene.frame_current -= 1


def toggle_rotation_locks(
    bone: PoseBone,
    mode: str,
    locks: Optional[List[bool]] = None
) -> None:

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


def update_panel(self, context: Context) -> None:
    """Update tab in which to place the panel"""
    try:
        # Ensure 'panels' is defined or imported
        # from .ui import panels  # Import panels from the appropriate module

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


def setup_bone_for_conversion(context: Context, bone: PoseBone) -> None:
    """Make only a specified bone selected and active before conversion"""
    bpy.ops.pose.select_all(action='DESELECT')
    context.object.data.bones.active = bone.bone
    bone.select = True
    dprint(f"### Working on bone '{bone.name}' ###")


def prepare_bone_locks(bone: PoseBone) -> Optional[List[bool]]:
    """Store and remove rotation locks for a bone before conversion."""
    preserve_locks = bpy.context.scene.CRM_Properties.preserveLocks

    if preserve_locks:
        locks = get_rotation_locks(bone)
        toggle_rotation_locks(bone, 'OFF')
        dprint(" |  # Backed up and unlocked rotations")
        return locks
    else:
        toggle_rotation_locks(bone, 'OFF')
        dprint(" |  # Unlocked rotations")
        return None


def setup_initial_keyframe(bone: PoseBone) -> str:
    """
    Jump at the start frame and place a keyframe to make sure no unwanted
    changes in animation happen from there to the next keyframe.
    Returns the original rotation mode.
    """
    original_rmode = bone.rotation_mode
    bpy.ops.screen.frame_jump(end=False)
    bone.rotation_mode = original_rmode
    bone.keyframe_insert(
        "rotation_mode",
        frame=1,
        group=bone.name
    )
    return original_rmode


def convert_frame_rotation(
    context: Context,
    bone: PoseBone,
    original_rmode: str
) -> None:
    """Convert rotation mode for a single frame."""
    target_rmode = context.scene.CRM_Properties.targetRmode
    current_frame = context.scene.frame_current

    # Set to original rmode and keyframe it
    bone.rotation_mode = original_rmode
    bone.keyframe_insert(
        "rotation_mode",
        frame=current_frame,
        group=bone.name
    )
    dprint(f" |  |  # '{bone.name}' Rmode set to {bone.rotation_mode}")

    # Copy global transform
    bpy.ops.object.copy_global_transform()
    dprint(
        f" |  |  # Copied '{bone.name}' Global Transform as {original_rmode}"
    )

    # Set to target rmode, and keyframe it
    bone.rotation_mode = target_rmode
    bone.keyframe_insert(
        "rotation_mode",
        frame=current_frame,
        group=bone.name
    )
    dprint(f" |  |  # Rmode set to {bone.rotation_mode}")

    # Paste transform
    bpy.ops.object.paste_transform(method='CURRENT', use_mirror=False)
    dprint(
        f" |  |  # Pasted '{bone.name}' Global Transform as "
        f"{bone.rotation_mode}"
    )

    # Keyframe all rotation properties
    for path in (
        "rotation_axis_angle",
        "rotation_euler",
        "rotation_mode",
        "rotation_quaternion",
    ):
        bone.keyframe_insert(data_path=path)
    dprint(f" |  |  # Keyframed '{bone.name}' rotations")


def process_bone_conversion(context: Context, bone: PoseBone) -> None:
    """Process the complete conversion for a single bone."""
    CRM_Properties = context.scene.CRM_Properties

    setup_bone_for_conversion(context, bone)
    dprint(f" # Target Rmode will be {CRM_Properties.targetRmode}")

    locks = prepare_bone_locks(bone)

    original_rmode = setup_initial_keyframe(bone)

    # Process each frame
    while context.scene.frame_current <= context.scene.frame_end:
        current_frame = context.scene.frame_current
        dprint(f" |  # Jumped to frame {current_frame}")

        update_progress(context)

        # Convert rotation for this frame
        convert_frame_rotation(context, bone, original_rmode)

        # Move to next frame
        jump_next_frame(context)
        if current_frame == context.scene.frame_current:
            break

    # Restore locks if needed
    if CRM_Properties.preserveLocks:
        toggle_rotation_locks(bone, 'ON', locks)
        dprint(" |  # Reverted rotation locks")

    dprint(f" # No more keyframes on '{bone.name}'.#")


def init_progress(context: Context, total_bones: int) -> None:
    """Initialize the progress tracking."""
    global _progress_counter
    scene = context.scene
    total_frames = scene.frame_end - scene.frame_start + 1
    progress_max = total_bones * total_frames
    _progress_counter = 0
    context.window_manager.progress_begin(0, progress_max)


def update_progress(context: Context) -> None:
    """Update the progress counter and progress bar"""
    global _progress_counter
    _progress_counter += 1
    context.window_manager.progress_update(_progress_counter)


def finish_progress(context: Context) -> None:
    """Finish the progress tracking."""
    context.window_manager.progress_end()


def store_initial_state(context: Context) -> None:
    """Store the initial state before conversion."""
    scene = context.scene
    selection = list(context.selected_pose_bones)
    scene["crm_initial_frame"] = scene.frame_current
    scene["crm_initial_selection"] = selection

    # Store the active pose bone, not the active bone
    if context.active_pose_bone:
        scene["crm_initial_active"] = context.active_pose_bone
    elif selection:
        scene["crm_initial_active"] = selection[0]
    else:
        scene["crm_initial_active"] = None


def restore_initial_state(context: Context) -> None:
    """Restore the initial state after conversion."""
    CRM_Properties = context.scene.CRM_Properties
    scene = context.scene

    if CRM_Properties.jumpInitFrame:
        initial_frame = scene.get('crm_initial_frame', 1)
        context.scene.frame_current = initial_frame

    if CRM_Properties.preserveSelection:
        # Restore selection from stored data
        selected_bones = scene.get('crm_initial_selection', [])
        initial_active_bone = scene.get('crm_initial_active', None)

        bpy.ops.pose.select_all(action='DESELECT')
        for bone in selected_bones:
            bone.select = True

        # Set active bone - handle both PoseBone and Bone objects
        if initial_active_bone:
            if hasattr(initial_active_bone, 'bone'):
                # It's a PoseBone, get the underlying Bone
                context.object.data.bones.active = initial_active_bone.bone
            else:
                # It's already a Bone
                context.object.data.bones.active = initial_active_bone

    # Clean up stored data
    scene.pop("crm_initial_frame", None)
    scene.pop("crm_initial_active", None)
    scene.pop("crm_initial_selection", None)
