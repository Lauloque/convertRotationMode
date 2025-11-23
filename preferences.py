# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
import platform
from bpy.types import AddonPreferences
from bpy.props import BoolProperty, StringProperty
from .ui import update_panel


class AddonPreferences(AddonPreferences):
    """Addon's preferences"""
    bl_idname = __package__

    developer_print: bpy.props.BoolProperty(
        name="Enable Developer Log in System Console",
        description=(
            "Helps with debugging issues in the addon.\n"
            "Please use this for any bug report.\n"
            "Keep it disabled for better performances."
        ),
        default=False
    )

    category: StringProperty(
        name="Tab Category",
        description="Choose the addon's tab (default: Animation).",
        default="Animation",
        update=update_panel,
    )

    def draw(self, context):
        """Draw addon's preferences"""
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "category", text="Tab Name")
        if "Windows" in platform.system():
            row = layout.row()
            row.prop(self, "developer_print")
            row.operator("wm.console_toggle", icon="CONSOLE", text="")
