# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
from .operators import CRM_OT_convert_rotation_mode
from .properties import CRM_Props
from .ui import (
    VIEW3D_PT_convert_rotation_mode,
    VIEW3D_PT_Rmodes_recommendations,
)
from .preferences import AddonPreferences

classes = (
    CRM_Props,
    CRM_OT_convert_rotation_mode,
    VIEW3D_PT_convert_rotation_mode,
    VIEW3D_PT_Rmodes_recommendations,
    AddonPreferences,
)


def register():
    """Register classes then rotation modes PointerProperty"""
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"Error registering class {cls.__package__}: {e}")
    bpy.types.Scene.CRM_Properties = bpy.props.PointerProperty(type=CRM_Props)


def unregister():
    """Unregister in reverse order of registation"""
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"Error unregistering class {cls.__package__}: {e}")
    del bpy.types.Scene.CRM_Properties
