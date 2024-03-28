import unittest
import os
import sys
import pytest

sys.path.insert(1, '../nohide_space')

from main import create_file_if_not_exists

test_file_path = "./test.txt"


def file_exist(path):
    check_file = os.path.isfile(path)
    print(check_file, " exist")


class TestCreateFileIfNotExist:
    def test_create_file_if_not_exists(self):
        os.remove(test_file_path)
        assert os.path.isfile(test_file_path) == False
        assert create_file_if_not_exists(test_file_path) == 1
        assert os.path.isfile(test_file_path)
        assert create_file_if_not_exists(test_file_path) == 0
        assert create_file_if_not_exists("") == -1


if __name__ == '__main__':
    unittest.main()
