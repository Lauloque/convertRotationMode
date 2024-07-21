import os
import zipfile
import re
import ast
import subprocess

def get_base_path():
    return os.path.dirname(os.path.abspath(__file__))

def read_version_init(base_path):
    init_path = os.path.join(base_path, 'convert_Rotation_Mode', '__init__.py')
    if not os.path.exists(init_path):
        raise FileNotFoundError(f"File not found: {init_path}")
    with open(init_path, 'r') as file:
        content = file.read()
    print("Content of __init__.py:", content)  # Debugging line
    # Extract the version from the bl_info dictionary
    match = re.search(r'\"version\"\s*:\s*\((\d+),\s*(\d+),\s*(\d+)\)', content)
    if match:
        return tuple(map(int, match.groups()))
    raise ValueError("Version not found in __init__.py")

def read_version_toml(base_path):
    toml_path = os.path.join(base_path, 'convert_Rotation_Mode', 'blender_manifest.toml')
    if not os.path.exists(toml_path):
        raise FileNotFoundError(f"File not found: {toml_path}")
    with open(toml_path, 'r') as file:
        content = file.read()
    print("Content of blender_manifest.toml:", content)  # Debugging line
    match = re.search(r'^version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', content, re.MULTILINE)
    if match:
        return tuple(map(int, match.groups()))
    raise ValueError("Version not found in blender_manifest.toml")

def normalize_version(version):
    return tuple(int(part) for part in version)

def update_version_init(base_path, version):
    version_str = f'\"version\": ({version[0]}, {version[1]}, {version[2]})'
    init_path = os.path.join(base_path, 'convert_Rotation_Mode', '__init__.py')
    with open(init_path, 'r') as file:
        content = file.read()
    content = re.sub(r'\"version\"\s*:\s*\(\d+, \d+, \d+\)', version_str, content)
    with open(init_path, 'w') as file:
        file.write(content)

def update_version_toml(base_path, version):
    version_str = f'version = "{version[0]}.{version[1]}.{version[2]}"'
    toml_path = os.path.join(base_path, 'convert_Rotation_Mode', 'blender_manifest.toml')
    with open(toml_path, 'r') as file:
        content = file.read()
    content = re.sub(r'^version\s*=\s*"\d+\.\d+\.\d+"', version_str, content, flags=re.MULTILINE)
    with open(toml_path, 'w') as file:
        file.write(content)

def create_zip(base_path, version):
    # zip_filename = os.path.join(base_path, 'Releases', f'convert_Rotation_Mode_v{version[0]}-{version[1]}-{version[2]}.zip')
    # os.makedirs(os.path.dirname(zip_filename), exist_ok=True)
    # with zipfile.ZipFile(zip_filename, 'w') as zipf:
    #     for root, dirs, files in os.walk(os.path.join(base_path, 'convert_Rotation_Mode')):
    #         for file in files:
    #             file_path = os.path.join(root, file)
    #             arcname = os.path.relpath(file_path, os.path.join(base_path, 'convert_Rotation_Mode'))
    #             zipf.write(file_path, arcname)
    command = '"C:\\AppInstall\\Blender\\stable\\blender-4.2.0-stable.a51f293548ad\\blender.exe" '
    command += '--command extension build --source-dir "C:\\Users\\Lauloque\\Documents\\Repositories\\convertRotationMode\\convert_Rotation_Mode" '
    command += f'--output-filepath "C:\\Users\\Lauloque\\Documents\\Repositories\\convertRotationMode\\Releases\\extension__convert_Rotation_Mode_v{version[0]}-{version[1]}-{version[2]}.zip"'
    subprocess.call(command)

def main():
    base_path = get_base_path()
    try:
        version_init = read_version_init(base_path)
        version_toml = read_version_toml(base_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return

    if normalize_version(version_init) != normalize_version(version_toml):
        print("Version mismatch detected.")
        new_version = input("Enter new version (X.Y.Z): ")
        try:
            version_tuple = tuple(map(int, new_version.split('.')))
            if len(version_tuple) != 3:
                raise ValueError
        except ValueError:
            print("Invalid version format.")
            return
        
        update_version_init(base_path, version_tuple)
        update_version_toml(base_path, version_tuple)
    else:
        version_tuple = version_init
    
    create_zip(base_path, version_tuple)
    print(f"Release zip created: convert_Rotation_Mode_v{version_tuple[0]}-{version_tuple[1]}-{version_tuple[2]}.zip")

if __name__ == '__main__':
    main()