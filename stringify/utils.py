import binascii
import json
import logging
import os
import platform
import shlex
import subprocess

logger = logging.getLogger(__name__)

PRESETS_FILE = os.path.expanduser("~/.stringify.json")


def load_presets():
    if os.path.exists(PRESETS_FILE):
        with open(PRESETS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_presets(presets):
    with open(PRESETS_FILE, 'w') as f:
        json.dump(presets, f, indent=2)


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


def gather_code(file_list, preview_length=None):
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
        else:
            result += f"--- {file_path} ---\n[Directory]\n\n"
    return result


def interactive_mode(initial_args):
    args = initial_args.copy()
    while True:
        print(args)
        if not validate_rsync_args(args):
            print("Error: Invalid rsync arguments. Please try again.")
            continue

        file_list = run_rsync(args)
        print("\nCurrent file list:")
        for file in file_list:
            if os.path.isfile(file):
                print(file)
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


def print_tree(file_list):
    tree = {}
    for file_path in file_list:
        parts = file_path.split(os.sep)
        current = tree
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
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
            if subtree:
                print_tree_recursive(subtree, new_prefix)

    print_tree_recursive(tree)


def copy_to_clipboard(text, file_list):
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
        print(f"Copied {len(text.splitlines())} lines from {len(file_list)} files to clipboard.")
    except Exception as e:
        print(f"Failed to copy to clipboard: {e}")
