# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
from bpy.types import Panel
from bpy.types import Context
from .utils import is_any_pose_bone_selected
from .bl_logger import logger


class VIEW3D_PT_convert_rotation_mode(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Animation"
    bl_label = "Convert Rotation Mode"

    def draw(self, context: Context) -> None:
        """Draw main panel"""
        layout = self.layout

        scene = context.scene
        CRM_Properties = scene.CRM_Properties

        col = layout.column(align=True)
        col.label(text="Target Rotation Mode")
        col.prop(CRM_Properties, "targetRmode", text="")

        if context.preferences.addons.find("copy_global_transform") == -1:
            row = col.row(align=False)
            row.alignment = 'CENTER'
            row.label(text="Required:", icon="ERROR")
            row = col.row(align=False)
            row.alignment = 'CENTER'
            row.label(text="'Copy Global Transform'")
            row = col.row(align=False)
            row.alignment = 'CENTER'
            row.operator(
                "preferences.addon_enable",
                text="Enable"
            ).module="copy_global_transform"
            row = col.row(align=False)
            row.alignment = 'CENTER'
            row.label(text="---")
        if not is_any_pose_bone_selected():
            col = layout.column(align=True)
            col.label(text="Please select a bone!", icon="ERROR")

        col = layout.column(align=True)
        col.operator("crm.convert_rotation_mode", text="Convert!")
        col.prop(CRM_Properties, "jumpInitFrame")
        col.prop(CRM_Properties, "preserveLocks")
        col.prop(CRM_Properties, "preserveSelection")


class VIEW3D_PT_Rmodes_recommendations(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Animation"
    bl_parent_id = "VIEW3D_PT_convert_rotation_mode"
    bl_label = "Rotation Modes Cheat Sheet"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context: Context) -> None:
        """Draw recommendations panel"""
        layout = self.layout

        grid = layout.grid_flow(columns=2, align=True, even_columns=True)
        grid.label(text="# Bone/Body Part")
        grid.label(text="COG")
        grid.label(text="Hip")
        grid.label(text="Leg")
        grid.label(text="Shoulders")
        grid.label(text="Arm Upper")
        grid.label(text="Arm Lower")
        grid.label(text="Wrist")
        grid.label(text="Fingers")
        grid.label(text="Spine Base")
        grid.label(text="Spine Mid")
        grid.label(text="Chest")
        grid.label(text="Neck")
        grid.label(text="Head")
        grid.label(text="# Rotation Mode")
        grid.label(text="ZXY")
        grid.label(text="YZX")
        grid.label(text="ZXY")
        grid.label(text="YZX")
        grid.label(text="YXZ")
        grid.label(text="ZYX (or YZX)")
        grid.label(text="ZYX (or YZX)")
        grid.label(text="YZX")
        grid.label(text="ZXY")
        grid.label(text="YZX")
        grid.label(text="ZXY")
        grid.label(text="YXZ")
        grid.label(text="YXZ")


panels = [
    VIEW3D_PT_convert_rotation_mode,
    VIEW3D_PT_Rmodes_recommendations,
]


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
        logger.error(
            "\n[{}]\n{}\n\nError:\n{}".format(__package__, message, e)
        )
