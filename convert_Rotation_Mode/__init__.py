# SPDX-License-Identifier: GPL-3.0-or-later
import bpy



def register():
    """Register"""
    # --- Always register zone ---
    # only things that are safe in background mode AND still useful there
    # e.g. properties or operators that make sense to run from CLI
    # add your Always-zone registration here

    # --- GUI-mode-only register zone ---
    if not bpy.app.background:
        # Move only the internal imports used by this GUI-mode-only zone
        # e.g. from . import ui, panels, gpu_stuff
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

        # Add your GUI-mode-only registration here
        for cls in classes:
            try:
                bpy.utils.register_class(cls)
            except Exception as e:
                print(f"Error registering class {cls.__package__}: {e}")
        bpy.types.Scene.CRM_Properties = bpy.props.PointerProperty(type=CRM_Props)
        pass
    else:
        print(f"[{__package__}] skipping GUI-mode-only registration: Blender is in background mode.")



def unregister():
    """Unregister"""
    # --- GUI-mode-only unregister zone ---
    if not bpy.app.background:
        # add your GUI-mode-only unregister here
        for cls in reversed(classes):
            try:
                bpy.utils.unregister_class(cls)
            except Exception as e:
                print(f"Error unregistering class {cls.__package__}: {e}")
        del bpy.types.Scene.CRM_Properties
        pass

    # --- Always unregister zone ---
    # Add your Always-zone unregister here
