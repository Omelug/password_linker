import unittest
import os
import sys
from unittest.mock import mock_open, patch

import pytest

lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')
sys.path.append(lib_dir)
from lib.file_format import *

test_file_path = "./test.txt"


def is_empty_json(file_path):
    with open(file_path, 'r') as file:
        content = file.read().strip()
        return content == "{}"

def file_exist(path):
    check_file = os.path.isfile(path)
    print(check_file, " exist")


class TestCreateFileIfNotExist(unittest.TestCase): #create_file_if_not_exists
    def test_create_file_if_not_exists(self):
        try:
            self.assertTrue(create_file_if_not_exists(test_file_path))
            self.assertTrue(os.path.isfile(test_file_path))
            self.assertFalse(create_file_if_not_exists(test_file_path))
            with pytest.raises(SystemExit) as e:
                create_file_if_not_exists("")
            assert e.type == SystemExit
            assert e.value.code == 1
        finally:
            os.remove(test_file_path)

    def test_create_empty_json(self): #create_empty_json
        empty_path = "./empty_json.json"
        try:
            assert create_empty_json(empty_path) == 1
            assert is_empty_json(empty_path)
            with pytest.raises(SystemExit) as e:
                create_empty_json("")
            assert e.type == SystemExit
            assert e.value.code == 1
        finally:
            os.remove(empty_path)

class TestLoadConfig(unittest.TestCase): #load_config
    @patch("builtins.open", new_callable=mock_open, read_data='{"key1": "value1"}')
    @patch("builtins.exit")
    def test_load_config_success(self, mock_exit, mock_open):
        result = load_config("config.json", "key1", "default_value")
        self.assertEqual(result, "value1")
        mock_exit.assert_not_called()

    @patch("builtins.open", new_callable=mock_open, read_data='{"key1": "value1"}')
    @patch("builtins.exit")
    def test_load_config_key_not_found(self, mock_exit, mock_open):
        result = load_config("config.json", "nonexistent_key", "default_value")
        self.assertEqual(result, "default_value")
        mock_exit.assert_not_called()

    @patch("builtins.open", side_effect=FileNotFoundError)
    @patch("builtins.exit")
    @patch("lib.file_format.create_empty_json", side_effect=lambda x: None)
    def test_load_config_file_not_found(self, mock_exit, mock_open):
        load_config("config.json", "key1", "default_value")
        mock_exit.assert_called_once_with(1)

    @patch("builtins.open", new_callable=mock_open, read_data='{"key1awdwadaw"')
    @patch("builtins.exit")
    @patch("lib.file_format.create_empty_json", side_effect=lambda x: None)
    @patch("logging.critical")
    def test_load_config_file_not_found(self,mock_logging_critical, n, mock_exit, mock_open):
        load_config("config.json", "key1", "default_value")
        mock_logging_critical.assert_called_once_with("Invalid JSON format in config file:", "config.json")
        mock_exit.assert_called_once_with(1)

class TestUpdateConfig(unittest.TestCase):

    @patch("lib.file_format.create_file_if_not_exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_update_config_non_existing_file(self, mock_json_dump, mock_open, mock_create_file):
        update_config("config.json", "key1", "value1")

        positional_args, keyword_args = mock_json_dump.call_args
        assert (positional_args[0] == {'key1': 'value1'})

    @patch("lib.file_format.create_file_if_not_exists", return_value=False)
    @patch("builtins.open", new_callable=mock_open, read_data='{"key1": "old_value"}')
    @patch("json.dump")
    def test_update_config_existing_key(self, mock_json_dump,mock_open, mock_create_file):
        update_config("config.json", "key1", "new_value")

        positional_args, keyword_args = mock_json_dump.call_args
        assert (positional_args[0] == {'key1': 'new_value'})
class TestAddUnique(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open)
    def test_add_new_needle(self, mock_open):
        mock_open.return_value.read.return_value = ""
        result = add_unique("test_file.txt", "needle")
        self.assertTrue(result)
        mock_open.return_value.write.assert_called_once_with("needle\n")

    @patch("builtins.open", new_callable=mock_open, read_data='needle\n')
    def test_add_already_in(self, mock_open):
        result = add_unique("test_file.txt", "needle")
        self.assertFalse(result)
        mock_open.return_value.write.assert_not_called()


class TestDownloadWithWget(unittest.TestCase):
    pass
class TestPrintJsonFile(unittest.TestCase):
    pass