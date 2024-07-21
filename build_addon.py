import shutil, os

# Target folder where to copy the addon's content.
# I use a custom directory to avoid having to reinstall addons at each new Blender version
# If you want to do the same, don't forget to add that path to Blender > Edit menu > Preferences > File Paths tab > Scripts

targetFolder="C:\\AppInstall\\Blender\\MyScripts\\addons"

# Input files and folders. See examples after ::
# Folders will be copied with their full content.
# Put them between quotation marks, one per line, and increment the number between [ ]
# You can write in absolute and relative paths, I chose relative for simplicity.

thingsToCopy=[
   "convert_Rotation_Mode"
   ]

## DEBUG
# print(__file__)
# print(os.path.join(os.path.dirname(__file__)))
# print()

# Ensure the target directory exists
if not os.path.exists(targetFolder):
    os.makedirs(targetFolder)
    print(f"Created directory '{targetFolder}'.")


for item in thingsToCopy:
    src_path = os.path.join(os.path.dirname(__file__), item)
    dest_path = os.path.join(targetFolder, item)
    
    if os.path.isdir(src_path):
        # Remove the destination directory if it exists
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)
    
    if os.path.isdir(src_path):
        # Copy directory and its contents
        try:
            shutil.copytree(src_path, dest_path)
            print(f"Copied directory '{item}' to '{targetFolder}'.")
        except Exception as e:
            print(f"Couldn't copy directory '{item}' to '{targetFolder}': {e}")
    else:
        # Copy individual file
        try:
            shutil.copy(src_path, dest_path)
            print(f"Copied file '{item}' to '{targetFolder}'.")
        except Exception as e:
            print(f"Couldn't copy file '{item}' to '{targetFolder}': {e}")