# SPDX-License-Identifier: GPL-3.0-or-later
### CLEANUP
# bl_info = {
#     "name": "Convert Rotation Mode",
#     "author": "Loïc \"Lauloque\" Dautry",
#     "version": (1, 4, 3),
#     "blender": (4, 2, 0),
#     "description": "Change the rotation mode of the selected bones and preserve the animation or poses you already made.",
#     "location": "3D Viewport → Sidebar → Animation Tab (Pose Mode only)",
#     "category": "Animation",
#     "support": 'COMMUNITY',
#     "doc_url": "https://github.com/L0Lock/convertRotationMode",
#     "tracker_url": "https://github.com/L0Lock/convertRotationMode/issues",
# }

import bpy
from .operators import CRM_OT_convert_rotation_mode
from .properties import CRM_Props
from .ui import VIEW3D_PT_convert_rotation_mode, VIEW3D_PT_Rmodes_recommandations
from .preferences import AddonPreferences

classes = (
    CRM_Props,
    CRM_OT_convert_rotation_mode,
    VIEW3D_PT_convert_rotation_mode,
    VIEW3D_PT_Rmodes_recommandations,
    AddonPreferences,
)

def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"Error registering class {cls.__package__}: {e}")
    bpy.types.Scene.CRM_Properties = bpy.props.PointerProperty(type=CRM_Props)

def unregister():
    for cls in reversed(classes):  # Unregister in reverse order of registration
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"Error unregistering class {cls.__package__}: {e}")
    del bpy.types.Scene.CRM_Properties
