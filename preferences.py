# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
import platform
from bpy.types import AddonPreferences
from bpy.props import BoolProperty, StringProperty
from .ui import update_panel
import logging


def update_developer_print(self, context):
    """Enable or disable logging based on preference"""
    from .bl_logger import logger
    if self.developer_print:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.CRITICAL + 1)


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
        default=False,
        update=update_developer_print
    ) # pyright: ignore[reportInvalidTypeForm]

    category: StringProperty(
        name="Tab Category",
        description="Choose the addon's tab (default: Animation).",
        default="Animation",
        update=update_panel,
    ) # pyright: ignore[reportInvalidTypeForm]

    def draw(self, context):
        """Draw addon's preferences"""
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "category", text="Tab Name")
        row = layout.row()
        row.prop(self, "developer_print")
        if "Windows" in platform.system():
            row.operator("wm.console_toggle", icon="CONSOLE", text="")
        else:
            split = layout.split(factor=0.35)
            split.label(text="")
            split.label(
                text="For Mac and Linux, you need to start Blender from the terminal to see the logs.",
                icon="INFO"
            )
