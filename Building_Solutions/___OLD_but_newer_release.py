import os
import zipfile
import re
import shutil
import subprocess
import argparse
from colors import printcol, Red, Cyan, Green, LightYellow, Orange 

extension_folder = 'convert_Rotation_Mode'
path_to_blender = 'C:\\AppInstall\\Blender\\stable\\blender-4.3.2-stable.32f5fdce0a0a\\blender.exe'

def get_base_path():
    return os.path.dirname(os.path.abspath(__file__))


def read_version_init(base_path):
    """ Extracts version from __init__.py """
    init_path = os.path.join(base_path, extension_folder, '__init__.py')
    if not os.path.exists(init_path):
        raise FileNotFoundError(f"File not found: {init_path}")
    with open(init_path, 'r') as file:
        content = file.read()
    match = re.search(r'[\'"]version[\'"]\s*:\s*\((\d+),\s*(\d+),\s*(\d+)\)', content)
    if match:
        return tuple(map(int, match.groups()))
    raise ValueError("Version not found in __init__.py")


def read_version_toml(base_path):
    """ Extracts version from blender_manifest.toml """
    toml_path = os.path.join(base_path, extension_folder, 'blender_manifest.toml')
    if not os.path.exists(toml_path):
        raise FileNotFoundError(f"File not found: {toml_path}")
    with open(toml_path, 'r') as file:
        content = file.read()
    match = re.search(r'^version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', content, re.MULTILINE)
    if match:
        return tuple(map(int, match.groups()))
    raise ValueError("Version not found in blender_manifest.toml")


def get_existing_versions(base_path):
    """ Returns a list of all versions (in tuples) found in the Releases folder, sorted. """
    releases_dir = os.path.join(base_path, "Releases")
    if not os.path.exists(releases_dir):
        return []

    version_pattern = re.compile(rf'extension_{extension_folder}_v(\d+)-(\d+)-(\d+)\.zip')
    existing_versions = []

    for filename in os.listdir(releases_dir):
        match = version_pattern.match(filename)
        if match:
            version = tuple(map(int, match.groups()))
            existing_versions.append(version)

    return sorted(existing_versions)

def check_zip_exists(base_path, version):
    """ Checks if the zip file for the current version exists in the Releases folder. """
    releases_dir = os.path.join(base_path, "Releases")
    zip_filename = f"extension_{extension_folder}_v{version[0]}-{version[1]}-{version[2]}.zip"
    return os.path.exists(os.path.join(releases_dir, zip_filename))


def update_version_files(base_path, version):
    """ Updates the version in __init__.py and blender_manifest.toml """
    version_str = f'"version": ({version[0]}, {version[1]}, {version[2]})'
    init_path = os.path.join(base_path, extension_folder, '__init__.py')
    with open(init_path, 'r') as file:
        content = file.read()
    content = re.sub(r'"version"\s*:\s*\(\d+, \d+, \d+\)', version_str, content)
    with open(init_path, 'w') as file:
        file.write(content)

    version_str = f'version = "{version[0]}.{version[1]}.{version[2]}"'
    toml_path = os.path.join(base_path, extension_folder, 'blender_manifest.toml')
    with open(toml_path, 'r') as file:
        content = file.read()
    content = re.sub(r'^version\s*=\s*"\d+\.\d+\.\d+"', version_str, content, flags=re.MULTILINE)
    with open(toml_path, 'w') as file:
        file.write(content)


def create_dev_copy(base_path):
    """ Creates a '_dev' copy of the extension and updates metadata. """
    dev_folder = extension_folder + "_dev"
    dev_path = os.path.join(base_path, dev_folder)

    if os.path.exists(dev_path):
        shutil.rmtree(dev_path)
    shutil.copytree(os.path.join(base_path, extension_folder), dev_path)

    # Modify __init__.py
    init_path = os.path.join(dev_path, '__init__.py')
    with open(init_path, 'r') as file:
        content = file.read()
    content = re.sub(r'("name"\s*:\s*)"([^"]+)"', r'\1"\2_dev"', content)
    content = re.sub(r'("id"\s*:\s*)"([^"]+)"', r'\1"\2_dev"', content)
    with open(init_path, 'w') as file:
        file.write(content)

    # Modify blender_manifest.toml
    toml_path = os.path.join(dev_path, 'blender_manifest.toml')
    with open(toml_path, 'r') as file:
        content = file.read()
    content = re.sub(r'^(name\s*=\s*)"([^"]+)"', r'\1"\2_dev"', content, flags=re.MULTILINE)
    content = re.sub(r'^(id\s*=\s*)"([^"]+)"', r'\1"\2_dev"', content, flags=re.MULTILINE)
    with open(toml_path, 'w') as file:
        file.write(content)

    return dev_folder


def create_zip(base_path, version, source_folder):
    """ Builds the extension using Blender's `--command extension build` tool. """
    if not os.path.exists(f'{base_path}\\Releases'):
        os.mkdir(f'{base_path}\\Releases')

    output_name = f'extension_{source_folder}_v{version[0]}-{version[1]}-{version[2]}.zip'
    command = f'{path_to_blender} --factory-startup --command extension build '
    command += f'--source-dir "{base_path}\\{source_folder}" '
    command += f'--output-filepath "{base_path}\\Releases\\{output_name}"'
    subprocess.call(command)
    printcol(Green, f"Release zip created: {output_name}")

def install_extension(base_path, version, is_dev):
    """ Installs the created zip file into Blender. """
    releases_dir = os.path.join(base_path, "Releases")
    
    # Determine zip filename
    zip_filename = f"extension_{extension_folder}_v{version[0]}-{version[1]}-{version[2]}.zip"
    if is_dev:
        zip_filename = f"extension_{extension_folder}_dev_v{version[0]}-{version[1]}-{version[2]}.zip"
        command = [
            path_to_blender, "--command", "extension", "loop_methods_dev"
        ]
    else:
        command = [
            path_to_blender, "--command", "extension", "loop_methods"
        ]
    
    zip_path = os.path.join(releases_dir, zip_filename)

    if not os.path.exists(zip_path):
        printcol(Red, f"Error: Zip file not found: {zip_path}")
        return

    printcol(Cyan, f"Removing old extension: {zip_filename}")
    subprocess.call(command)

    # Install using Blender's extension install command
    command = [
        path_to_blender, "--command", "extension", "install-file", "--repo my_extensions"
        "--enable", zip_path  # Auto-enable after installation
    ]

    printcol(Cyan, f"Installing extension: {zip_filename}")
    subprocess.call(command)
    printcol(Green, "Installation completed.")


def main():
    parser = argparse.ArgumentParser(description="Blender Extension Release Script")
    parser.add_argument("--dev", action="store_true", help="Create a development build with '_dev' suffix.")
    parser.add_argument("--install", "-I", action="store_true", help="Installs the created extension into Blender")
    args = parser.parse_args()

    base_path = get_base_path()

    if not os.path.isfile(path_to_blender):
        printcol(Red, f"Error: Blender Executable not found in:\n    `{path_to_blender}`")
        return
    elif not os.path.isdir(os.path.join(base_path, extension_folder)):
        printcol(Red, f"Error: Extension not found in:\n    `{base_path}\\{extension_folder}`")
        return
    else:
        printcol(Cyan, f"Found Blender Executable and Extension. Proceeding!")

    version_init = read_version_init(base_path)
    version_toml = read_version_toml(base_path)
    
    # Check if zip exists for the current version
    if check_zip_exists(base_path, version_init) and not args.dev:
        existing_versions = get_existing_versions(base_path)
        
        # Filter versions starting from the current version
        starting_index = existing_versions.index(version_init)
        versions_from_current = existing_versions[starting_index:]

        # Display versions from the current one onward
        existing_versions_str = [
            f"{v[0]}.{v[1]}.{v[2]}{' (current)' if v == version_init else ''}" for v in versions_from_current
        ]

        printcol(Orange, f"A release with version {version_init[0]}.{version_init[1]}.{version_init[2]} already exists.")
        printcol(LightYellow, f"Existing versions from current: {', '.join(existing_versions_str)}")

        while True:
            response = input("Do you want to (O)verwrite, (I)ncrement version, or (C)ancel? (O/I/C): ").strip().lower()
            if response == 'o':
                break  # Proceed with overwriting
            elif response == 'i':
                new_version = input("Enter new version (X.Y.Z): ").strip()
                try:
                    version_tuple = tuple(map(int, new_version.split('.')))
                    if len(version_tuple) != 3:
                        raise ValueError
                    update_version_files(base_path, version_tuple)  # Now we update the files
                    version_init = version_tuple  # Update the version_init to the new version
                    break
                except ValueError:
                    printcol(Orange, "Invalid version format. Try again.")
            elif response == 'c':
                printcol(LightYellow, "Operation canceled.")
                return
            else:
                printcol(Orange, "Invalid input. Please enter O, I, or C.")

    elif args.dev:
        # Define paths
        dev_folder = os.path.join(base_path, extension_folder + "_dev")
        releases_dir = os.path.join(base_path, "Releases")

        # Remove the dev folder if it exists
        if os.path.exists(dev_folder):
            printcol(Orange, f"Removing old dev folder: {dev_folder}")
            shutil.rmtree(dev_folder)

        # Find and delete any existing _dev zip file
        version_pattern = re.compile(rf'extension_{extension_folder}_dev_v\d+-\d+-\d+\.zip')
        dev_zip_files = [f for f in os.listdir(releases_dir) if version_pattern.match(f)]
        
        for dev_zip in dev_zip_files:
            dev_zip_path = os.path.join(releases_dir, dev_zip)
            printcol(Orange, f"Removing old dev zip: {dev_zip_path}")
            os.remove(dev_zip_path)

        printcol(Cyan, "Running in development mode. Overwriting dev zip if exists.")

    source_folder = create_dev_copy(base_path) if args.dev else extension_folder
    create_zip(base_path, version_init, source_folder)

    if args.install:
        install_extension(base_path, version_init, args.dev)

if __name__ == '__main__':
    main()
