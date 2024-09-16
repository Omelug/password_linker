import argparse
import logging
import os
import sys
import tempfile

import lib.io_tubes as io_tubes

__author__ = 'Omelug'
__date__ = '2024'
__description__ = """Change format of files (same like all other scripts)"""

def get_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_format', "-in_for", type=str, required=True)
    parser.add_argument('--out_format', "-out_for", type=str, required=True)
    return parser.parse_args(args)

def run(args, config=None):
    script_name = os.path.basename(__file__)
    logging.info(f"--> {script_name}")
    ARGS = get_args(args[2:])

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file_path = tmp_file.name
        tmp_file.write(sys.stdin.read().encode())

    tmp_file_path = io_tubes.convert_to_format(tmp_file_path, ARGS.in_format, ARGS.out_format)
    for line in open(tmp_file_path, 'r'):
        print(line, end='')


