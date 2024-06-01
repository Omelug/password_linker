import unittest
import os
import sys

lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')
sys.path.append(lib_dir)

from io import StringIO
from lib.logfile import *
from lib.file_regex import *


class GetRegex(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(get_regex("salt"), '.+?')

    def test_not_none(self):
        self.assertIsNone(get_regex("not known value"))

class FileRegexToRegex(unittest.TestCase):

    def test_long_path(self):
        path = "/home/kali/Desktop/JetBrains/PyCharm/passwordList/rsc/data/edited/dr7_users/md5:pass.txt"
        self.assertEqual(file_regex_to_regex(path), '.{32}:.*?')

    def test_invalid_path(self):
        self.assertEqual(file_regex_to_regex("/edited/dr7_users/test:pass.txt"), 'test:.*?')

    def test_no_change(self):
        self.assertEqual(file_regex_to_regex("no_change"), "no_change")

class PrintFileRegex(unittest.TestCase):
    def test_basic(self):
        stdout_saved = sys.stdout

        sys.stdout = StringIO()
        print_file_regex(["pass:sha1.txt", "pass:md5.txt"])
        actual_output = sys.stdout.getvalue()

        sys.stdout = stdout_saved
        self.assertEqual(actual_output, ".*?:.{40}\n.*?:.{32}\n")


class GetFileRegex(unittest.TestCase):
    def test_base(self):
        path = "/home/kali/Desktop/JetBrains/PyCharm/passwordList/rsc/data/edited/dr7_users/md5:pass.txt"
        self.assertEqual(get_file_regex(path), 'md5:pass')

    def test_invalid_path(self):
        self.assertEqual(get_file_regex("/edited/dr7_users/test.txt"), 'test')

    def test_no_change(self):
        self.assertEqual(get_file_regex("no_change"), 'no_change')
