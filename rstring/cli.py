import argparse
import logging
import os

from .utils import (
    load_presets, save_presets, check_rsync, run_rsync, validate_rsync_args,
    gather_code, interactive_mode, get_tree_string, copy_to_clipboard,
    get_default_preset, set_default_preset, parse_gitignore
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    if not check_rsync():
        print("Error: rsync is not installed on this system. Please install rsync and try again.")
        return

    parser = argparse.ArgumentParser(description="Stringify code with rsync and manage presets.", allow_abbrev=False)
    parser.add_argument("-p", "--preset", help="Use a saved preset")
    parser.add_argument("-sp", "--save-preset", type=str, metavar="NAME", help="Save the command as a preset")
    parser.add_argument("-lp", "--list-presets", action="store_true", help="List all saved presets")
    parser.add_argument("-dp", "--delete-preset", help="Delete a saved preset")
    parser.add_argument("-sdp", "--set-default-preset", help="Set the default preset")
    parser.add_argument("-i", "--interactive", action="store_true", help="Enter interactive mode")
    parser.add_argument("-nc", "--no-clipboard", action="store_true", help="Don't copy output to clipboard")
    parser.add_argument("-pl", "--preview-length", type=int, metavar="N",
                        help="Show only the first N lines of each file")
    parser.add_argument("-s", "--summary", action="store_true", help="Print a summary including a tree of files")
    parser.add_argument("-id", "--include-dirs", action="store_true",
                        help="Include empty directories in output and summary")
    parser.add_argument("-ng", "--no-gitignore", action="store_false", dest="use_gitignore",
                        help="Don't use .gitignore patterns")

    args, unknown_args = parser.parse_known_args()

    presets = load_presets()

    if args.list_presets:
        print("Saved presets:")
        for name, preset in presets.items():
            print(f"  {'*' if preset.get('is_default', False) else ' '} {name}: {' '.join(preset['args'])}")
        return

    if args.delete_preset:
        if args.delete_preset in presets:
            del presets[args.delete_preset]
            save_presets(presets)
            print(f"Preset '{args.delete_preset}' deleted.")
        else:
            print(f"Preset '{args.delete_preset}' not found.")
        return

    if args.set_default_preset:
        set_default_preset(presets, args.set_default_preset)
        return

    preset_name = args.preset or get_default_preset(presets) if not unknown_args else None
    if preset_name:
        preset = presets.get(preset_name)
        if preset:
            rsync_args = preset['args']
        else:
            print(f"Error: Preset '{preset_name}' not found.")
            return
    else:
        rsync_args = []

    rsync_args.extend(unknown_args)

    if args.save_preset:
        name = args.save_preset
        presets[name] = {'is_default': False, 'args': rsync_args}
        save_presets(presets)
        print(f"Preset '{name}' saved.")
        return

    if args.use_gitignore:
        gitignore_path = os.path.join(os.getcwd(), '.gitignore')
        if os.path.exists(gitignore_path):
            gitignore_patterns = parse_gitignore(gitignore_path)
            rsync_args = gitignore_patterns + rsync_args
        else:
            print("Warning: No .gitignore file found. Use --no-gitignore to ignore .gitignore patterns")

    if not any(arg for arg in rsync_args if not arg.startswith('--')):
        rsync_args.append('.')

    if not validate_rsync_args(rsync_args):
        print("Error: Invalid rsync arguments. Please check and try again.")
        return

    if args.interactive:
        rsync_args = interactive_mode(rsync_args, args.include_dirs)

    file_list = run_rsync(rsync_args)
    result = gather_code(file_list, args.preview_length, args.include_dirs)

    tree = get_tree_string(file_list, include_dirs=args.include_dirs, use_color=False)
    num_files = len([f for f in file_list if not os.path.isdir(f)])
    if args.summary:
        from datetime import datetime
        result_with_summary = ["### COLLECTION SUMMARY ###", "",
                               "The following files have been collected using the Rstring command.",
                               "Binary files are truncated to the first 32 bytes.", "", f"Files: {num_files}",
                               f"Lines: {len(result.splitlines())}",
                               f"Collected at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "", tree, "",
                               "### FILE CONTENTS ###", result]

        result = "\n".join(result_with_summary)

    if args.no_clipboard:
        print()
        print(result)
    else:
        colored_tree = get_tree_string(file_list, include_dirs=args.include_dirs)
        print(colored_tree) if len(colored_tree) > 0 else None
        copy_to_clipboard(result)

    if not args.no_clipboard:
        action = f"Collected {len(result.splitlines())} lines from {num_files}" if args.no_clipboard else f"Copied {len(result.splitlines())} lines from {num_files} files to clipboard"
        if preset_name:
            preset = presets.get(preset_name) if preset_name else None
            if ' '.join(rsync_args) != ' '.join(preset['args']):
                if 'gitignore_patterns' in locals() and ' '.join(gitignore_patterns + preset['args']) != ' '.join(
                        rsync_args):
                    print(f"{action} using preset '{preset_name}' with modified rsync options: {' '.join(rsync_args)}")
                else:
                    print(f"{action} using preset '{preset_name}' modified by .gitignore")
            else:
                print(f"{action} using preset '{preset_name}'")
        else:
            if 'gitignore_patterns' in locals():
                print(
                    f"{action} using custom rsync options modified by .gitignore: {' '.join(rsync_args).replace(' '.join(gitignore_patterns), '')}")
            else:
                print(f"{action} using custom rsync options: {' '.join(rsync_args)}:")


if __name__ == '__main__':
    main()
