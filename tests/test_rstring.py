import subprocess
from unittest.mock import patch, MagicMock, mock_open

import pytest
import yaml
import tempfile
import shutil
import os
import sys

# Add the parent directory to the path so we can import rstring
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rstring import utils, cli
from rstring.utils import (
    load_presets, save_presets, check_rsync, run_rsync, validate_rsync_args,
    gather_code, interactive_mode, get_tree_string, copy_to_clipboard,
    get_default_preset, set_default_preset, parse_gitignore, is_binary
)
from rstring.cli import parse_target_directory, main


@pytest.fixture
def temp_config(tmp_path):
    config_file = tmp_path / '.rstring.yaml'
    config_file.touch()
    with patch('rstring.utils.PRESETS_FILE', str(config_file)):
        yield config_file
    if config_file.exists():
        config_file.unlink()


def test_load_presets(temp_config):
    test_preset = {'test_preset': {'args': ['--include=*.py']}}
    temp_config.write_text(yaml.dump(test_preset))

    presets = utils.load_presets()
    assert presets == test_preset


def test_save_presets(temp_config):
    test_preset = {'test_preset': {'args': ['--include=*.py']}}
    utils.save_presets(test_preset)

    saved_preset = yaml.safe_load(temp_config.read_text())
    assert saved_preset == test_preset


def test_check_rsync():
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        assert utils.check_rsync() == True


def test_load_presets_invalid_yaml(temp_config):
    temp_config.write_text('invalid: yaml: :]')

    presets = utils.load_presets()
    assert presets == {}


def test_load_presets_file_not_found(temp_config):
    temp_config.unlink()
    mock_default_content = yaml.dump({'default_preset': {'args': ['--include=*.py']}})

    with patch('rstring.utils.PRESETS_FILE', 'nonexistent_file'):
        with patch('rstring.utils.DEFAULT_PRESETS_FILE', 'default_presets.yaml'):
            with patch('builtins.open', mock_open(read_data=mock_default_content)) as mock_file:
                presets = utils.load_presets()

                assert presets == {'default_preset': {'args': ['--include=*.py']}}
                mock_file.assert_any_call('default_presets.yaml', 'r')
                mock_file.assert_any_call('nonexistent_file', 'w')
                mock_file().write.assert_called_once_with(mock_default_content)


def test_run_rsync():
    mock_output = (
        "drwxr-xr-x          4,096 2023/04/01 12:00:00 .\n"
        "-rw-r--r--          1,234 2023/04/01 12:00:00 file1.py\n"
        "-rw-r--r--          2,345 2023/04/01 12:00:00 file2.py\n"
        "drwxr-xr-x          4,096 2023/04/01 12:00:00 subdir/\n"
        "-rw-r--r--          3,456 2023/04/01 12:00:00 subdir/file3.py\n"
    )
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(stdout=mock_output, stderr="")
        file_list = utils.run_rsync(["--include=*.py", "."])
        assert file_list == ["file1.py", "file2.py", "subdir/file3.py"]
        mock_run.assert_called_once_with(
            ["rsync", "-ain", "--list-only", "--include=*.py", "."],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )


def test_validate_rsync_args():
    with patch('rstring.utils.run_rsync') as mock_run_rsync:
        mock_run_rsync.return_value = ["file1.py", "file2.py"]
        assert utils.validate_rsync_args(["--include=*.py", "."]) == True

        mock_run_rsync.side_effect = subprocess.CalledProcessError(1, "rsync")
        assert utils.validate_rsync_args(["--invalid-arg"]) == False


@pytest.mark.parametrize("file_path, expected", [
    ("/path/to/text.txt", False),
    ("/path/to/binary.exe", True),
])
def test_is_binary(file_path, expected):
    with patch('builtins.open', mock_open(read_data=b'\x00' if expected else b'text')):
        assert utils.is_binary(file_path) == expected


def test_gather_code():
    file_list = ["/path/to/file1.py", "/path/to/file2.py"]
    file_contents = {
        "/path/to/file1.py": b"print('Hello')",
        "/path/to/file2.py": b"print('World')"
    }

    def mock_open_file(filename, *args, **kwargs):
        return mock_open(read_data=file_contents[filename])()

    with patch('builtins.open', side_effect=mock_open_file):
        with patch('rstring.utils.is_binary', return_value=False):
            with patch('os.path.isfile', return_value=True):
                result = utils.gather_code(file_list)
                assert "--- /path/to/file1.py ---" in result
                assert "print('Hello')" in result
                assert "--- /path/to/file2.py ---" in result
                assert "print('World')" in result


def test_interactive_mode():
    with patch('builtins.input') as mock_input:
        mock_input.side_effect = ['a', '*.txt', 'd']
        with patch('rstring.utils.validate_rsync_args', return_value=True):
            with patch('rstring.utils.run_rsync', return_value=['file1.txt']):
                result = utils.interactive_mode(['--include=*.py'])
                assert result == ['--include=*.py', '--include', '*.txt']


def test_print_tree():
    file_list = ['dir1/file1.py', 'dir1/dir2/file2.py', 'file3.py']

    def mock_isdir(path):
        path = path[2:] if path.startswith('./') else path
        return path in ['', 'dir1', 'dir1/dir2'] or path.replace('\\', '/') in ['', 'dir1', 'dir1/dir2']

    def mock_isfile(path):
        return path in file_list or path.replace('\\', '/') in file_list

    def mock_abspath(path):
        return '/tests' if path == '.' else f"/tests/{path}"

    with patch('os.path.isdir', side_effect=mock_isdir):
        with patch('os.path.isfile', side_effect=mock_isfile):
            with patch('os.path.abspath', side_effect=mock_abspath):
                output = utils.get_tree_string(file_list, include_dirs=False, use_color=False)

    expected_output = (
        "tests\n"
        "├── dir1\n"
        "│   ├── dir2\n"
        "│   │   └── file2.py\n"
        "│   └── file1.py\n"
        "└── file3.py"
    )
    assert output.strip() == expected_output.strip()


@pytest.mark.parametrize("system, command", [
    ("Darwin", "pbcopy"),
    ("Windows", "clip"),
    ("Linux", "xclip"),
])
def test_copy_to_clipboard(system, command):
    test_text = "Test clipboard content"
    with patch('platform.system', return_value=system):
        with patch('subprocess.run') as mock_run:
            utils.copy_to_clipboard(test_text)
            mock_run.assert_called_once()
            assert mock_run.call_args[0][0][0] == command


def test_main(temp_config):
    test_args = ['rstring', '--preset', 'test_preset']
    test_preset = {'test_preset': {'args': ['--include=*.py']}}
    temp_config.write_text(yaml.dump(test_preset))

    mock_gathered_code = 'print("Hello")\n' * 26

    with patch('sys.argv', test_args):
        with patch('rstring.utils.check_rsync', return_value=True):
            with patch('rstring.cli.gather_code', return_value=mock_gathered_code):
                with patch('rstring.cli.copy_to_clipboard') as mock_copy:
                    cli.main()
                    mock_copy.assert_called_once()
                    mock_copy.assert_called_with(mock_gathered_code)


def test_parse_target_directory():
    """Test the parse_target_directory function."""
    # Test -C flag
    target_dir, remaining = parse_target_directory(['-C', '/tmp', '--include=*.py'])
    assert target_dir == '/tmp'
    assert remaining == ['--include=*.py']

    # Test --directory flag
    target_dir, remaining = parse_target_directory(['--directory', '/tmp', '--include=*.py'])
    assert target_dir == '/tmp'
    assert remaining == ['--include=*.py']

    # Test --directory= format
    target_dir, remaining = parse_target_directory(['--directory=/tmp', '--include=*.py'])
    assert target_dir == '/tmp'
    assert remaining == ['--include=*.py']

    # Test positional directory (when it exists)
    with tempfile.TemporaryDirectory() as temp_dir:
        target_dir, remaining = parse_target_directory([temp_dir, '--include=*.py'])
        assert target_dir == os.path.abspath(temp_dir)
        assert remaining == ['--include=*.py']

    # Test no directory specified
    target_dir, remaining = parse_target_directory(['--include=*.py'])
    assert target_dir == os.path.abspath('.')
    assert remaining == ['--include=*.py']

    # Test error case
    with pytest.raises(ValueError):
        parse_target_directory(['-C'])


@patch('rstring.cli.run_rsync')
@patch('rstring.cli.gather_code')
@patch('rstring.cli.copy_to_clipboard')
@patch('rstring.cli.get_tree_string')
@patch('rstring.cli.load_presets')
@patch('rstring.cli.check_rsync')
def test_main_with_target_directory(mock_check_rsync, mock_load_presets, mock_get_tree_string,
                                   mock_copy_to_clipboard, mock_gather_code, mock_run_rsync):
    """Test main function with target directory functionality."""
    mock_check_rsync.return_value = True
    mock_load_presets.return_value = {}
    mock_run_rsync.return_value = ['test.py']
    mock_gather_code.return_value = 'test content'
    mock_get_tree_string.return_value = 'tree'

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test file
        test_file = os.path.join(temp_dir, 'test.py')
        with open(test_file, 'w') as f:
            f.write('print("hello")')

        # Test -C flag
        with patch('sys.argv', ['rstring', '-C', temp_dir, '--include=*.py', '--no-clipboard']):
            with patch('os.chdir') as mock_chdir:
                main()
                # Should change to target dir and then back to original
                assert mock_chdir.call_count == 2
                mock_chdir.assert_any_call(temp_dir)

        # Test positional argument
        with patch('sys.argv', ['rstring', temp_dir, '--include=*.py', '--no-clipboard']):
            with patch('os.chdir') as mock_chdir:
                main()
                # Should change to target dir and then back to original
                assert mock_chdir.call_count == 2
                mock_chdir.assert_any_call(temp_dir)


def test_main_with_nonexistent_directory():
    """Test main function with non-existent directory."""
    with patch('rstring.cli.check_rsync', return_value=True):
        with patch('rstring.cli.load_presets', return_value={}):
            with patch('sys.argv', ['rstring', '-C', '/nonexistent', '--include=*.py']):
                with patch('builtins.print') as mock_print:
                    main()
                    mock_print.assert_called_with("Error: Directory '/nonexistent' does not exist.")
