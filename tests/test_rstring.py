import subprocess
from unittest.mock import patch, MagicMock, mock_open

import pytest
import yaml
from rstring import utils, cli


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


def test_print_tree(capsys):
    file_list = ['dir1/file1.py', 'dir1/dir2/file2.py', 'file3.py']

    def mock_isfile(path):
        return path in file_list or path.replace('\\', '/') in file_list

    with patch('os.path.isfile', side_effect=mock_isfile):
        utils.print_tree(file_list)

    captured = capsys.readouterr()
    expected_output = (
        "├── dir1\n"
        "│   ├── file1.py\n"
        "│   └── dir2\n"
        "│       └── file2.py\n"
        "└── file3.py\n"
    )
    assert captured.out.strip() == expected_output.strip()


@pytest.mark.parametrize("system, command", [
    ("Darwin", "pbcopy"),
    ("Windows", "clip"),
    ("Linux", "xclip"),
])
def test_copy_to_clipboard(system, command):
    test_text = "Test clipboard content"
    file_list = ["file1.py"]
    num_files = 1
    with patch('platform.system', return_value=system):
        with patch('subprocess.run') as mock_run:
            utils.copy_to_clipboard(test_text, file_list, num_files)
            mock_run.assert_called_once()
            assert mock_run.call_args[0][0][0] == command


def test_main(temp_config):
    test_args = ['rstring', '--preset', 'test_preset']
    test_preset = {'test_preset': {'args': ['--include=*.py']}}
    temp_config.write_text(yaml.dump(test_preset))

    mock_file_list = ['file1.py', 'file2.py', 'file3.py', 'file4.py', 'file5.py', 'file6.py', 'file7.py']
    mock_gathered_code = 'print("Hello")\n' * 26

    with patch('sys.argv', test_args):
        with patch('rstring.utils.check_rsync', return_value=True):
            with patch('rstring.cli.run_rsync', return_value=mock_file_list):
                with patch('rstring.cli.gather_code', return_value=mock_gathered_code):
                    with patch('rstring.cli.copy_to_clipboard') as mock_copy:
                        cli.main()
                        mock_copy.assert_called_once()
                        mock_copy.assert_called_with(mock_gathered_code, mock_file_list, 7)
