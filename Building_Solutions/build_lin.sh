#!/bin/bash
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the parent directory (addon root)
cd "$SCRIPT_DIR/.." || exit 1

# Now run the command with correct relative paths
/home/lauloque/Apps/Graphics/BlenderLauncher/stable/blender-5.0.0-stable.a37564c4df7a/blender --factory-startup --command extension build --source-dir "." --output-dir "Releases"

echo "Press enter to continue..."
read