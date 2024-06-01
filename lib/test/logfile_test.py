import unittest
import os
import sys
import datetime
from unittest.mock import mock_open, patch
import sys
import pytest

lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')
sys.path.append(lib_dir)
from lib.logfile import *


class Init(unittest.TestCase):

    @patch("file_format.create_empty_json", side_effect=lambda x: None)
    @patch("builtins.exit")
    def test_no_json(self, mock_exit, mock_empty):
        invalid_paths = ["invalid.fad", "../../invalid.txt"]

        for path in invalid_paths:
            with self.subTest(path=path):
                LogFile(path)
                mock_exit.assert_called_once_with(1)
                mock_exit.reset_mock()
                if os.path.exists(path):
                    os.remove(path)

    @patch("file_format.create_empty_json", side_effect=lambda x: None)
    @patch("builtins.exit")
    def test_invalid_dir(self, mock_exit, mock_empty):
        LogFile("./LogDirectory")
        mock_exit.assert_called_once_with(1)

    def test_not_exist(self):
        LogFile("test.json")


class New(unittest.TestCase):

    @patch("file_format.now_string", return_value="now")
    @patch("json.dump")
    @patch("builtins.open", new_callable=mock_open, read_data='{}')
    @patch("uuid.uuid4", return_value="123456")
    def test_new_item(self, mock_uuid, mock_open, mock_json_dump, mock_now):
        unique_id = LogFile("test.json").new(args=sys.argv)  #new( in file, returned id
        assert (unique_id == "123456")
        positional_args, keyword_args = mock_json_dump.call_args
        assert ({
                    "uuid": "123456",
                    "start_time": "now",
                    "input_args": sys.argv,
                    "progress": {
                        "status": "started",
                        "errors": []
                    }
                } == positional_args[0][0])

    def setUp(self):
        self.log_file_path = "new.json"
        self.log_file = LogFile(self.log_file_path)

    def tearDown(self):
        if os.path.exists(self.log_file_path):
            os.remove(self.log_file_path)

    def test_empty(self):
        self.log_file_path = "new.json"
        self.log_file = LogFile(self.log_file_path)
        args = [f"{__name__}", "arg1", "arg2", "arg3", "arg4"]
        unique_id = self.log_file.new(args)

        data = self.log_file.get_or_none(unique_id)
        self.assertIsNotNone(data)

        if os.path.exists(self.log_file_path):
            os.remove(self.log_file_path)

        self.assertEqual(data["uuid"], str(unique_id))
        self.assertEqual(data["input_args"], args)
        self.assertEqual(data["progress"]["status"], "started")
        self.assertEqual(data["progress"]["errors"], [])
        self.assertTrue(isinstance(data["start_time"], str))
        try:
            datetime.datetime.strptime(data["start_time"], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            print("Error: Provided datetime string is not in the correct format.")

    def test_empty_no_args(self):
        unique_id = self.log_file.new([])
        data = self.log_file.get_or_none(unique_id)
        self.assertIsNotNone(data)
        self.assertEqual(data["uuid"], str(unique_id))
        self.assertEqual(data["input_args"], [])

class Get_OR(unittest.TestCase):
    test = """{
        "uuid": "123456",
        "start_time": "now",
        "input_args": sys.argv,
        "progress": {
            "status": "started",
            "errors": []
        }
    }"""

    @patch("builtins.open", new_callable=mock_open, read_data='[{"uuid": "123456"}]')
    def test_create_or_found(self, mock_open):
        lf = LogFile("test.json")
        self.assertEqual(lf.get_or_none("123456"), {"uuid": "123456"})
        self.assertEqual(lf.get_or_create("123456"), {"uuid": "123456"})

    @patch("builtins.open", new_callable=mock_open, read_data="{}")
    def test_create_or_not_found(self, mock_open):
        lf = LogFile("test.json")
        self.assertIsNone(lf.get_or_none("123456"))
        #FIXME tady je problem, ze to ma zmenit file self.assertEqual(lf.get_or_create("123456"), {"uuid": "123456"})

class Add_to_List(unittest.TestCase):
    pass

class Update(unittest.TestCase):
    def setUp(self):
        self.log_file_path = "update.json"
        self.log_file = LogFile(self.log_file_path)
        self.unique_id = self.log_file.new(["arg1", "arg2"])

    def tearDown(self):
        if os.path.exists(self.log_file_path):
            os.remove(self.log_file_path)

    def test_update(self):
        self.assertEqual(self.log_file.update(self.unique_id, "start_time", "NaN"), True)
        data = self.log_file.get_or_none(self.unique_id)
        self.assertIsNotNone(data)
        self.assertEqual(data["start_time"], "NaN")

        self.log_file.update(self.unique_id, ["progress", "status"], "ahoj")
        data = self.log_file.get_or_none(self.unique_id)
        self.assertIsNotNone(data)
        self.assertEqual(data["progress"]["status"], "ahoj")

class add_error(unittest.TestCase):
    pass

class add_error_msg(unittest.TestCase):
    pass

