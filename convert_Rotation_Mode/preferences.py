# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
from bpy.types import AddonPreferences, Panel
from bpy.props import BoolProperty, StringProperty
from .utils import update_panel 

### CLEANUP
# def update_panel(self, context):
#     message = "Convert Rotation Mode: Updating Panel locations has failed"
#     try:
#         for panel in panels:
#             if "bl_rna" in panel.__dict__:
#                 bpy.utils.unregister_class(panel)

#         for panel in panels:
#             panel.bl_category = context.preferences.addons[__name__].preferences.category
#             bpy.utils.register_class(panel)

#     except Exception as e:
#         print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
#         pass
        
class AddonPreferences(AddonPreferences):
    bl_idname = __package__
    ### CLEANUP bl_idname = __name__

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

        row = layout.row()
        row.prop(self, "category")
        row.label(text="")
        row.prop(self, "devMode")

        row = layout.row()
        if context.preferences.addons.find("copy_global_transform") == -1:
            row.label(text="This addon requires the addon 'Copy Global Transform' by Sybren A. Stüvel.", icon="ERROR")
            row.operator("crm.enable_addon")
