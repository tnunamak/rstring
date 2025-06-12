import logging
import subprocess

logger = logging.getLogger(__name__)


def is_git_command_available():
    try:
        subprocess.run(['git', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def is_ignored_by_git(target_dir, file_path):
    try:
        logger.debug(f"Checking if {file_path} is ignored by git in {target_dir}")
        result = subprocess.run(
            ['git', 'check-ignore', '-q', file_path],
            cwd=target_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        logger.debug(f"Git check-ignore return code for {file_path}: {result.returncode}")
        return result.returncode == 0
    except subprocess.CalledProcessError:
        logger.debug(f"CalledProcessError for {file_path}")
        return False
    except Exception as e:
        logger.error(f"Error checking if {file_path} is ignored by git: {str(e)}")
        return False


def filter_ignored_files(target_dir, file_list):
    if not is_git_command_available():
        logger.warning("Git command is not available.")
        return file_list  # Return the original list if git is not available

    logger.debug(f"Filtering ignored files in {target_dir}")
    logger.debug(f"Original file list: {file_list}")
    filtered_list = [
        file_path for file_path in file_list
        if not is_ignored_by_git(target_dir, file_path)
    ]
    logger.debug(f"Filtered file list: {filtered_list}")
    return filtered_list