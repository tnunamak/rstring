import unittest
from unittest.mock import patch, MagicMock

from stringify import utils


class TestStringifyCode(unittest.TestCase):

    def test_load_presets(self):
        with patch('json.load') as mock_json_load:
            mock_json_load.return_value = {'test_preset': ['--include=*.py']}
            presets = utils.load_presets()
            self.assertEqual(presets, {'test_preset': ['--include=*.py']})

    def test_save_presets(self):
        with patch('json.dump') as mock_json_dump:
            utils.save_presets({'test_preset': ['--include=*.py']})
            mock_json_dump.assert_called_once()

    def test_check_rsync(self):
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            self.assertTrue(utils.check_rsync())


if __name__ == '__main__':
    unittest.main()
