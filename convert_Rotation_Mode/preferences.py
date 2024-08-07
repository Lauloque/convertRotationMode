# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
from bpy.types import AddonPreferences, Panel
from bpy.props import BoolProperty, StringProperty
from .utils import update_panel 
        
class AddonPreferences(AddonPreferences):
    bl_idname = __package__

    devMode: BoolProperty(
        name="Developer Mode",
        description='Enables all error tracking messages.',
        default=False,
    )

    category: StringProperty(
        name="Tab Category",
        description="Choose a name for the category of the panel (default: Animation).",
        default="Animation",
        update=update_panel,
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "category", text="Tab Name")
        layout.prop(self, "devMode", text="Dev Mode")


        
        if context.preferences.addons.find("copy_global_transform") == -1:
            row = layout.row(align=False)
            row.alignment = 'CENTER'
            row.label(text="This addon requires the addon 'Copy Global Transform' by Sybren A. Stüvel.", icon="ERROR")
            row = layout.row(align=False)
            row.alignment = 'CENTER'
            row.operator("preferences.addon_enable").module="copy_global_transform"
