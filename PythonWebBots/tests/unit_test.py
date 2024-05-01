import unittest
import os
import sys
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


class TestCreateFileIfNotExist:
    def test_create_file_if_not_exists(self):
        try:
            assert create_file_if_not_exists(test_file_path) == 1
            assert os.path.isfile(test_file_path)
            assert create_file_if_not_exists(test_file_path) == 0
            with pytest.raises(SystemExit) as e:
                create_file_if_not_exists("")
            assert e.type == SystemExit
            assert e.value.code == 1
        finally:
            os.remove(test_file_path)
class TestJsonFunctions:
    def test_create_empty_json(self):
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
class Test_Subbprocesses:
    def test_download_with_wget(self):
        assert download_with_wget("https://example.com/", "./") == True
        #TODO assert download_with_wget("https://example.com/nesmysl", "./") == False

if __name__ == '__main__':
    unittest.main()
