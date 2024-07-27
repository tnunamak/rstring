import binascii
import logging
import os
import platform
import shlex
import subprocess

import yaml

logger = logging.getLogger(__name__)

PRESETS_FILE = os.path.expanduser("~/.rstring.yaml")
DEFAULT_PRESETS_FILE = os.path.join(os.path.dirname(__file__), 'default_presets.yaml')


def load_presets():
    if os.path.exists(PRESETS_FILE):
        try:
            with open(PRESETS_FILE, 'r') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing {PRESETS_FILE}: {e}")
            print(f"Error parsing {PRESETS_FILE}. Using empty presets.")
        except Exception as e:
            logger.error(f"Error reading {PRESETS_FILE}: {e}")
            print(f"Error reading {PRESETS_FILE}. Using empty presets.")
    else:
        try:
            with open(DEFAULT_PRESETS_FILE, 'r') as df:
                content = df.read()
                with open(PRESETS_FILE, 'w') as f:
                    f.write(content)
                return yaml.safe_load(content) or {}
        except Exception as e:
            logger.error(f"Error reading or writing preset files: {e}")
            print(f"Error with preset files. Using empty presets.")
    return {}


def save_presets(presets):
    with open(PRESETS_FILE, 'w') as f:
        yaml.dump(presets, f)


def get_default_preset(presets):
    for name, preset in presets.items():
        if preset.get('is_default', False):
            return name
    return None


def set_default_preset(presets, preset_name):
    if preset_name not in presets:
        print(f"Error: Preset '{preset_name}' not found")
        return

    for name, preset in presets.items():
        preset['is_default'] = (name == preset_name)

    save_presets(presets)
    print(f"Default preset set to '{preset_name}'")


def parse_gitignore(gitignore_path):
    if not os.path.exists(gitignore_path):
        return []

    with open(gitignore_path, 'r') as f:
        lines = f.readlines()

    gitignore_patterns = ['--exclude=.git']
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            if line.startswith('/'):
                line = line[1:]
            if line.endswith('/'):
                gitignore_patterns.append(f"--exclude={line}*")
            else:
                gitignore_patterns.append(f"--exclude={line}")

    return gitignore_patterns


def check_rsync():
    try:
        subprocess.run(["rsync", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def run_rsync(args):
    cmd = ["rsync", "-ain", "--list-only"] + args
    logger.debug(f"Rsync command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.debug(f"Rsync stdout: {result.stdout}")
        logger.debug(f"Rsync stderr: {result.stderr}")
        return parse_rsync_output(result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error(f"Rsync command failed: {e}")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        raise


def validate_rsync_args(args):
    try:
        run_rsync(args)
        return True
    except subprocess.CalledProcessError:
        return False


def parse_rsync_output(output):
    file_list = []
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 5 and not line.endswith('/'):
            file_path = ' '.join(parts[4:])
            if file_path != '.':  # Exclude the root directory
                file_list.append(file_path)
    return file_list


def is_binary(file_path):
    try:
        with open(file_path, 'rb') as file:
            return b'\0' in file.read(1024)
    except IOError:
        return False


def gather_code(file_list, preview_length=None, include_dirs=False):
    result = ""
    for file_path in file_list:
        full_path = file_path
        if os.path.isfile(full_path):
            try:
                with open(full_path, 'rb') as file_content:
                    if is_binary(full_path):
                        if preview_length is None or preview_length > 0:
                            file_data = f"[Binary file, first 32 bytes: {binascii.hexlify(file_content.read(32)).decode()}]"
                    else:
                        file_data = file_content.read().decode('utf-8', errors='ignore')
                        file_data = '\n'.join(file_data.splitlines()[:preview_length])
                    if preview_length is None or preview_length > 0:
                        result += f"--- {file_path} ---\n{file_data}\n\n"
                    else:
                        result += f"--- {file_path} ---\n\n"
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
        elif include_dirs and os.path.isdir(full_path):
            result += f"--- {file_path} ---\n[Directory]\n\n"
    return result


def interactive_mode(initial_args, include_dirs=False):
    args = initial_args.copy()
    while True:
        print(args)
        if not validate_rsync_args(args):
            print("Error: Invalid rsync arguments. Please try again.")
            continue

        file_list = run_rsync(args)
        print("\nCurrent file list:")
        print_tree(file_list, include_dirs=include_dirs)
        print(f"\nCurrent rsync arguments: {' '.join(args)}")

        action = input("\nEnter an action (a)dd/(r)emove/(e)dit/(d)one: ").lower()
        if action in ['done', 'd']:
            break
        elif action in ['add', 'a']:
            pattern = input("Enter a pattern: ")
            args.extend(['--include', pattern])
        elif action in ['remove', 'r']:
            pattern = input("Enter a pattern: ")
            args.extend(['--exclude', pattern])
        elif action in ['edit', 'e']:
            args_str = input("Enter the new rsync arguments: ")
            new_args = shlex.split(args_str)
            if not any(arg for arg in new_args if not arg.startswith('--')):
                new_args.append('.')
            if validate_rsync_args(new_args):
                args = new_args
            else:
                print("Error: Invalid rsync arguments. Please try again.")
        else:
            print("Invalid action. Please enter 'a', 'r', 'e', or 'd'.")

    return args


def print_tree(file_list, include_dirs=False):
    tree = {}
    for file_path in file_list:
        parts = file_path.split(os.sep)
        current = tree
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        if include_dirs or os.path.isfile(file_path):
            current[parts[-1]] = {}

    def print_tree_recursive(node, prefix=""):
        items = list(node.items())
        for i, (name, subtree) in enumerate(items):
            if i == len(items) - 1:
                print(f"{prefix}└── {name}")
                new_prefix = prefix + "    "
            else:
                print(f"{prefix}├── {name}")
                new_prefix = prefix + "│   "
            if subtree or (include_dirs and os.path.isdir(os.path.join(*node.keys(), name))):
                print_tree_recursive(subtree, new_prefix)

    print_tree_recursive(tree)


def copy_to_clipboard(text, file_list, num_files):
    system = platform.system()
    try:
        if system == 'Darwin':  # macOS
            subprocess.run(['pbcopy'], input=text.encode('utf-8'), check=True)
        elif system == 'Windows':
            subprocess.run(['clip'], input=text.encode('utf-8'), check=True)
        elif system == 'Linux':
            try:
                subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode('utf-8'), check=True)
            except FileNotFoundError:
                subprocess.run(['xsel', '--clipboard', '--input'], input=text.encode('utf-8'), check=True)
        print(f"Copied {len(text.splitlines())} lines from {num_files} files to clipboard.")
    except Exception as e:
        print(f"Failed to copy to clipboard: {e}")
