#!/bin/bash
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the parent directory (addon root)
cd "$SCRIPT_DIR/.." || exit 1

# Now run the command with correct relative paths
if ! command -v blender >/dev/null 2>&1; then
    echo "Error: 'blender' was not found in PATH."
    exit 1
fi

blender --factory-startup --command extension build --source-dir "." --output-dir "Releases"

echo "Press enter to continue..."
read