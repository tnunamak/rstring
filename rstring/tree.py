import os

import colorama
from colorama import Fore, Style

colorama.init()


class Colors:
    RESET = Style.RESET_ALL
    BLUE = Fore.BLUE
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW


def get_tree_string(file_list, include_dirs=False, use_color=True):
    if not file_list:
        return ""

    common_prefix = os.path.commonprefix(file_list)
    if not os.path.isdir(common_prefix):
        common_prefix = os.path.dirname(common_prefix)

    if not common_prefix or common_prefix == '/':
        common_prefix = '.'

    root_name = os.path.basename(os.path.abspath(common_prefix))
    tree = {root_name: {}}

    for file_path in file_list:
        relative_path = os.path.relpath(file_path, common_prefix)
        parts = relative_path.split(os.sep)
        current = tree[root_name]
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        if include_dirs or os.path.isfile(file_path):
            current[parts[-1]] = {}

    def colorize(text, color):
        return f"{color}{text}{Colors.RESET}" if use_color else text

    def build_tree_string(node, path, prefix=""):
        lines = []
        items = sorted(node.items(), key=lambda x: (not os.path.isdir(os.path.join(path, x[0])), x[0]))
        for i, (name, subtree) in enumerate(items):
            is_last = (i == len(items) - 1)
            full_path = os.path.join(path, name)
            is_dir = os.path.isdir(full_path)
            is_executable = os.access(full_path, os.X_OK) and not is_dir

            if is_last:
                branch = "└── "
                new_prefix = prefix + "    "
            else:
                branch = "├── "
                new_prefix = prefix + "│   "

            if is_dir:
                name = colorize(name, Colors.BLUE)
            elif is_executable:
                name = colorize(name, Colors.GREEN)
            elif name.startswith('.'):
                name = colorize(name, Colors.YELLOW)

            lines.append(f"{prefix}{branch}{name}")

            if is_dir:
                lines.extend(build_tree_string(subtree, full_path, new_prefix))
        return lines

    result = [colorize(root_name, Colors.BLUE)]
    result.extend(build_tree_string(tree[root_name], common_prefix))
    return "\n".join(result)
