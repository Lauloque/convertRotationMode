# SPDX-License-Identifier: GPL-3.0-or-later
from typing import List, Optional, Union
import bpy
from bpy.types import Context, PoseBone, Bone
from .ui import panels
# from .progress_bar import (
#     init_progress,
#     update_progress,
#     finish_progress,
# )


def dprint(message: str) -> None:
    """Prints in the system console if the addon's developer printing is ON"""
    prefs = bpy.context.preferences.addons[__package__].preferences
    if prefs.developer_print:
        print(f"[Convert Rot Mode]: {message}")


def bake_all_frames(bone: PoseBone) -> None:
    """Bakes all frames of a bone"""
    scene = bpy.context.scene
    rotation_paths = ["rotation_mode"]

    # get first and last frame of anim fcurves and rotation paths list
    
    
    for path in rotation_paths:
        bone.keyframe_insert(data_path=path)


def get_list_frames(bone: Bone) -> List[float]:
    """
    Returns the list of frames with rotation keyframes on the selected bones
    """
    # context = bpy.context
    list_frames: List[float] = []

    armature = bone.id_data
    # ----FOR FUTURE MULTIBONE SUPPORT----
    # list_armatures = []
    # selected_pose_bones = context.selected_pose_bones
    # for bone in selected_pose_bones:
    #     armature = bone.id_data
    #     if armature not in list_armatures:
    #         list_armatures.append(armature)
    # for armature in list_armatures:

    fcurves = armature.animation_data.action.fcurves

    for curve in fcurves:
        # skip non-rotation curves
        if "rotation" not in curve.data_path:
            pass

        keyframe_points = curve.keyframe_points

        for keyframe in keyframe_points:
            frame = keyframe.co[0]
            if frame not in list_frames:
                list_frames.append(frame)

    return sorted(list_frames)


def deselect_all_bones() -> None:
    """Deselect all bones"""
    for bone in bpy.context.selected_pose_bones:
        bone.bone.select = False


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
    deselect_all_bones()
    context.object.data.bones.active = bone.bone
    bone.bone.select = True
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


def setup_initial_keyframe(bone: PoseBone, first_frame: float) -> str:
    """
    Jump at the start frame and place a keyframe to make sure no unwanted
    changes in animation happen from there to the next keyframe.
    Returns the original rotation mode.
    """
    original_rmode = bone.rotation_mode
    scene = bpy.context.scene
    scene.frame_set(int(first_frame))
    # bpy.ops.screen.frame_jump(end=False)
    bone.rotation_mode = original_rmode
    bone.keyframe_insert(
        "rotation_mode",
        frame=int(first_frame),
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
    bone_name = bone.name

    # Set to original rmode and keyframe it
    bone.rotation_mode = original_rmode
    bone.keyframe_insert(
        "rotation_mode",
        frame=current_frame,
        group=bone.name
    )
    dprint(f" |  |  # '{bone_name}' Rmode set to {bone.rotation_mode}")

    # Copy global transform
    bpy.ops.object.copy_global_transform()
    dprint(
        f" |  |  # Copied '{bone_name}' Global Transform as {original_rmode}"
    )

    # Set to target rmode, and keyframe it
    bone.rotation_mode = target_rmode
    bone.keyframe_insert(
        "rotation_mode",
        frame=current_frame,
        group=bone_name
    )
    dprint(f" |  |  # Rmode set to {bone.rotation_mode}")

    # Paste transform
    bpy.ops.object.paste_transform(method='CURRENT', use_mirror=False)
    dprint(
        f" |  |  # Pasted '{bone_name}' Global Transform as "
        f"{bone.rotation_mode}"
    )

    # Keyframe all rotation properties
    rotation_paths = [
        "rotation_axis_angle",
        "rotation_euler",
        "rotation_mode",
        "rotation_quaternion",
    ]
    for path in rotation_paths:
        bone.keyframe_insert(data_path=path)
    dprint(f" |  |  # Keyframed '{bone_name}' rotations")


def process_bone_conversion(context: Context, bone: PoseBone) -> None:
    """Process the complete conversion for a single bone."""
    CRM_Properties = context.scene.CRM_Properties
    scene = context.scene
    # frame_end = scene.frame_end

    setup_bone_for_conversion(context, bone)
    dprint(f" # Target Rmode will be {CRM_Properties.targetRmode}")

    locks = prepare_bone_locks(bone)
    if CRM_Properties.bake_all_frames:
        bake_all_frames(current_bone)
    list_frames = get_list_frames(bone)
    original_rmode = setup_initial_keyframe(bone, list_frames[0])

    # Process each frame in the frames list
    for frame in list_frames:
        scene.frame_set(int(frame))
        dprint(f" |  # Jumped to frame {frame}")

        update_progress(context)

        convert_frame_rotation(context, bone, original_rmode)

        # CLEANUP
        # jump_next_frame(context)

        # if current_frame == context.scene.frame_current:
        #     break

    # Restore locks if needed
    if CRM_Properties.preserveLocks:
        toggle_rotation_locks(bone, 'ON', locks)
        dprint(" |  # Reverted rotation locks")

    dprint(f" # No more keyframes on '{bone.name}'.#")


def init_progress(context: Context, total_bones: int) -> None:
    """Initialize the progress tracking."""
    global _progress_counter
    scene = context.scene

    # Calculate total frames
    total_frames = scene.frame_end - scene.frame_start + 1
    progress_max = total_bones * total_frames

    # Safety checks
    if progress_max <= 0:
        dprint(
            f"Warning: Invalid progress_max ({progress_max}). Using fallback."
        )
        progress_max = total_bones  # Fallback to just bone count

    _progress_counter = 0

    try:
        context.window_manager.progress_begin(0, progress_max)
    except Exception as e:
        dprint(f"Failed to initialize progress bar: {e}")


def update_progress(context: Context) -> None:
    """Update the progress counter and progress bar"""
    global _progress_counter
    _progress_counter += 1
    try:
        context.window_manager.progress_update(_progress_counter)
    except Exception as e:
        dprint(f"Failed to update progress: {e}")


def finish_progress(context: Context) -> None:
    """Finish the progress tracking."""
    try:
        context.window_manager.progress_end()
        dprint("Progress bar finished successfully")
    except Exception as e:
        dprint(f"Failed to finish progress bar: {e}")


def store_initial_state(context: Context) -> None:
    """Store the initial state before conversion."""
    scene = context.scene
    selection = list(context.selected_pose_bones)
    scene["crm_initial_frame"] = scene.frame_current

    # Store bone names instead of bone objects
    scene["crm_initial_selection"] = [bone.name for bone in selection]

    # Store the active pose bone name, not the bone object
    if context.active_pose_bone:
        scene["crm_initial_active"] = context.active_pose_bone.name
    elif selection:
        scene["crm_initial_active"] = selection[0].name
    else:
        scene["crm_initial_active"] = ""


def restore_initial_state(context: Context) -> None:
    """Restore the initial state after conversion."""
    CRM_Properties = context.scene.CRM_Properties
    scene = context.scene

    if CRM_Properties.jumpInitFrame:
        initial_frame = scene.get('crm_initial_frame', 1)
        context.scene.frame_current = initial_frame

    if CRM_Properties.preserveSelection:
        # Restore selection from stored bone names
        selected_bone_names = scene.get('crm_initial_selection', [])
        initial_active_bone_name = scene.get('crm_initial_active', "")
        pose_bones = context.object.pose.bones
        data_bones = context.object.data.bones

        deselect_all_bones()

        # Select bones by name - use bone.bone.select for Blender 4.0+
        # Ensure we're working with strings
        if isinstance(selected_bone_names, (list, tuple)):
            for bone_name in selected_bone_names:
                bone_name_str = str(bone_name)
                dprint(f"Trying to select bone: '{bone_name_str}'")
                if bone_name_str in pose_bones:
                    pose_bones[bone_name_str].bone.select = True

        # Set active bone by name
        if initial_active_bone_name:
            active_bone_name_str = str(initial_active_bone_name)
            if active_bone_name_str and active_bone_name_str in data_bones:
                data_bones.active = data_bones[active_bone_name_str]

    # Clean up stored data
    scene.pop("crm_initial_frame", None)
    scene.pop("crm_initial_active", None)
    scene.pop("crm_initial_selection", None)
