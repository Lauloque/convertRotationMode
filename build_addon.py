import shutil, os

# Target folder where to copy the addon's content.
# I use a custom directory to avoid having to reinstall addons at each new Blender version
# If you want to do the same, don't forget to add that path to Blender > Edit menu > Preferences > File Paths tab > Scripts

targetFolder="C:\\AppInstall\\Blender\\MyScripts\\addons\\conver_Rotation_Mode"

# Input files and folders. See examples after ::
# Folders will be copied with their full content.
# Put them between quotation marks, one per line, and increment the number between [ ]
# You can write in absolute and relative paths, I chose relative for simplicity.

inputFiles=[
   "convert_Rotation_Mode.py"
   ]

## DEBUG
# print(__file__)
# print(os.path.join(os.path.dirname(__file__)))
# print()

# Ensure the target directory exists
if not os.path.exists(targetFolder):
    os.makedirs(targetFolder)
    print(f"Created directory '{targetFolder}'.")

for file in inputFiles:
    src_path = os.path.join(os.path.dirname(__file__), file)
    dest_path = os.path.join(targetFolder, file)
    try:
        shutil.copy(src_path, dest_path)
        print(f"copied '{file}' to '{targetFolder}'.")
    except Exception as e:
        print(f"Couldn't copy '{file}' to '{targetFolder}': {e}")
