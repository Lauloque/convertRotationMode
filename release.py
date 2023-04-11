from convert_Rotation_Mode import bl_info
import shutil

addonVersion = "-".join(str(x) for x in bl_info['version'])
blenderVersion = "-".join(str(x) for x in bl_info['blender'])
oldname = "convert_Rotation_Mode.py"
newName = f".\\releases\\convert_Rotation_Mode_v{addonVersion}_for_Blender{blenderVersion}.py"

shutil.copy2(oldname, newName)