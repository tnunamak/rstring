import binascii
import logging
import os
import platform
import shlex
import subprocess
import sys

logger = logging.getLogger(__name__)

from .tree import get_tree_string


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
    template = "--- {} ---\n{}\n\n"
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
                        # result += f"--- {file_path} ---\n{file_data}\n\n"
                        result += template.format(file_path, file_data)
                    else:
                        # result += f"--- {file_path} ---\n\n"
                        result += template.format(file_path, "")
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
        elif include_dirs and os.path.isdir(full_path):
            # result += f"--- {file_path} ---\n[Directory]\n\n"
            result += template.format(file_path, "[Directory]")
    return result[:-2]


def interactive_mode(initial_args, include_dirs=False, stdout=sys.stdout):
    args = initial_args.copy()
    while True:
        print(args, file=stdout)
        if not validate_rsync_args(args):
            print("Error: Invalid rsync arguments. Please try again.", file=sys.stderr)
            continue

        file_list = run_rsync(args)
        print("\nCurrent file list:", file=stdout)
        print(get_tree_string(file_list, include_dirs=include_dirs), file=stdout)
        print(f"\nCurrent rsync arguments: {' '.join(args)}", file=stdout)

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
                print("Error: Invalid rsync arguments. Please try again.", file=sys.stderr)
        else:
            print("Invalid action. Please enter 'a', 'r', 'e', or 'd'.", file=stdout)

    return args


def copy_to_clipboard(text):
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            subprocess.run(["pbcopy"], input=text, text=True, check=True)
        elif system == "Linux":
            subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True, check=True)
        elif system == "Windows":
            subprocess.run(["clip"], input=text, text=True, check=True)
        else:
            print(f"Unsupported platform: {system}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to copy to clipboard: {e}")
    except FileNotFoundError:
        if system == "Linux":
            print("xclip not found. Please install xclip to enable clipboard functionality.")
        else:
            print("Clipboard functionality not available.")
