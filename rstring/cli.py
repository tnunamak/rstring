import argparse
import logging
import os
import sys

from .utils import (
    check_rsync, run_rsync, validate_rsync_args,
    gather_code, interactive_mode, get_tree_string, copy_to_clipboard,
    parse_gitignore
)

from .git import filter_ignored_files

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_target_directory(args):
    """Parse target directory from arguments with -C flag and positional support."""
    # Look for -C/--directory flag first (use the last one if multiple)
    target_dir = None
    remaining_args = []
    i = 0

    while i < len(args):
        arg = args[i]
        if arg in ['-C', '--directory']:
            if i + 1 < len(args):
                target_dir = args[i + 1]
                i += 2  # Skip both flag and value
            else:
                raise ValueError("-C/--directory requires a directory argument")
        elif arg.startswith('--directory='):
            target_dir = arg.split('=', 1)[1]
            i += 1
        else:
            remaining_args.append(arg)
            i += 1

    # If no -C flag, check for positional directory argument (only the first non-flag arg)
    if target_dir is None and remaining_args:
        first_arg = remaining_args[0]
        if not first_arg.startswith('-') and os.path.isdir(first_arg):
            target_dir = first_arg
            remaining_args = remaining_args[1:]

    # Default to current directory
    if target_dir is None:
        target_dir = '.'

    return os.path.abspath(target_dir), remaining_args


def get_default_patterns():
    """Conservative default: include everything, let gitignore filter."""
    return ['--include=*/']


def main():
    if not check_rsync():
        print("Error: rsync is not installed on this system. Please install rsync and try again.", file=sys.stderr)
        return

    parser = argparse.ArgumentParser(
        description="Stringify code with rsync filtering.",
        epilog="""
Examples:
  rstring                           # All files (gitignore filtered)
  rstring --include='*.py'          # Only Python files
  rstring -C /path/to/project       # Different directory
  rstring --include='*/' --include='*.js' --exclude='test*'  # Complex patterns

For frequently used patterns, create shell aliases:
  alias rstring-py="rstring --include='*/' --include='*.py' --exclude='test*'"
  alias rstring-web="rstring --include='*/' --include='*.{js,css,html}'"
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        allow_abbrev=False
    )

    parser.add_argument("-C", "--directory", help="Change to directory before processing")
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

    # Parse target directory from -C flag or positional args
    try:
        if args.directory:
            target_dir = os.path.abspath(args.directory)
            rsync_args_base = unknown_args
        else:
            target_dir, rsync_args_base = parse_target_directory(unknown_args)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return

    # Validate target directory exists
    if not os.path.isdir(target_dir):
        print(f"Error: Directory '{target_dir}' does not exist.", file=sys.stderr)
        return

    # Use provided patterns or conservative default
    if rsync_args_base:
        rsync_args = rsync_args_base
    else:
        rsync_args = get_default_patterns()

    # Handle gitignore in target directory
    if args.use_gitignore:
        gitignore_path = os.path.join(target_dir, '.gitignore')
        if os.path.exists(gitignore_path):
            gitignore_patterns = parse_gitignore(gitignore_path)
            rsync_args = gitignore_patterns + rsync_args
        else:
            print(f"Warning: No .gitignore file found in {target_dir}. Use --no-gitignore to ignore .gitignore patterns", file=sys.stderr)

    # Add default source if none specified
    if not any(arg for arg in rsync_args if not arg.startswith('--')):
        rsync_args.append('.')

    # Change to target directory for rsync execution
    original_cwd = os.getcwd()
    try:
        os.chdir(target_dir)

        if not validate_rsync_args(rsync_args):
            print("Error: Invalid rsync arguments. Please check and try again.", file=sys.stderr)
            return

        if args.interactive:
            rsync_args = interactive_mode(rsync_args, args.include_dirs)

        file_list = run_rsync(rsync_args)

        # Apply git filtering if in a git repository
        try:
            file_list = filter_ignored_files(target_dir, file_list)
        except Exception as e:
            logger.warning(f"Git filtering failed: {e}")

        result = gather_code(file_list, args.preview_length, args.include_dirs)

        tree = get_tree_string(file_list, include_dirs=args.include_dirs, use_color=False)
        num_files = len([f for f in file_list if not os.path.isdir(f)])

    finally:
        os.chdir(original_cwd)

    if args.summary:
        from datetime import datetime
        lines = len(result.splitlines())
        chars = len(result)
        tokens = chars // 4  # Rough estimate: 1 token ≈ 4 characters
        result_with_summary = ["### COLLECTION SUMMARY ###", "",
                               "The following files have been collected using the rstring command.",
                               "Binary files are truncated to the first 32 bytes.", "", f"Files: {num_files}",
                               f"Lines: {lines}",
                               f"Characters: {chars:,}",
                               f"Tokens (est.): ~{tokens:,}",
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
        lines = len(result.splitlines())
        chars = len(result)
        tokens = chars // 4  # Rough estimate: 1 token ≈ 4 characters
        action = f"Collected {lines} lines ({chars:,} chars, ~{tokens:,} tokens) from {num_files}" if args.no_clipboard else f"Copied {lines} lines ({chars:,} chars, ~{tokens:,} tokens) from {num_files} files to clipboard"
        target_info = f" from {target_dir}" if target_dir != original_cwd else ""
        if 'RSTRING_TESTING' not in os.environ:
            print(f"{action}{target_info}")


if __name__ == "__main__":
    main()
