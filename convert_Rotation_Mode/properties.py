# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
from bpy.props import EnumProperty, BoolProperty
from bpy.types import PropertyGroup


class CRM_Props(PropertyGroup):
    targetRmode: EnumProperty(
        name='Target Rotation Mode',
        description='Target Rotation Mode for the conversion.',
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

    jumpInitFrame: BoolProperty(
        name="Preserve current frame",
        description='Preserve the current frame after conversion is done.',
        default=True
    )

    preserveLocks: BoolProperty(
        name="Preserve Locks",
        description="Preserves lock states on rotation channels.",
        default=True
    )

    preserveSelection: BoolProperty(
        name="Preserve Selection",
        description="Preserves selection.",
        default=True
    )

    bake_all_frames: BoolProperty(
        name="Bake all frames",
        description="Bakes and converts every frame instead of only keyframes "
                    "to prevent unexpected rotation changes between them, at "
                    "the cost of slower conversion and dense, harder-to-edit "
                    "animation curves.",
        default=False
    )

    simplify_curves: BoolProperty(
        name="Simplify Curves",
        description="Makes curves easier to edit after conversion by "
                    "simplifying them, which may slightly alter the original "
                    "unbaked rotation.",
        default=False
    )
