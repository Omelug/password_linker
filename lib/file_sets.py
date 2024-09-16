# Log list logffile.py
# for logffile

import os
import sys
import argparse
lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../lib')
sys.path.append(lib_dir)
import file_format
import subprocess
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

class Table(object):
    def __init__(self, r_list, c_list):
        self.r_list = list(r_list)
        self.c_list = list(c_list)
        self.data = [[0 for _ in range(len(c_list))] for _ in range(len(r_list))]


    def print(self):
        for row in range(len(self.r_list)):
            print(f"{self.c_list[row]:<80}", end='')
            for col in range(len(self.c_list)):
                print(f"{self.data[row][col]:.0f}\t",end='')
            print()

def compute_union_size(target_file, other_files):
    shell_script = os.path.join(script_dir, 'set_sh', 'union_size.sh')
    command = [shell_script, target_file] + other_files
    result = subprocess.run(command, capture_output=True, text=True)
    return int(result.stdout.strip())

def compute_intersection_size(target_file, other_file):
    shell_script = os.path.join(script_dir, 'set_sh', 'intersection_size.sh')
    command = [shell_script, target_file, other_file]
    result = subprocess.run(command, capture_output=True, text=True)
    return int(result.stdout.strip())

def print_header(list):
    for i, link in enumerate(list):
        print(f'{i}: {link}')
    print(" "*80, end='')
    for i, link in enumerate(list):
        print(f"{i}\t", end='')
    print()

def intersection_stats(r_link, c_list):
    table = Table(r_link, c_list)

    for i, row in enumerate(table.r_list):
        for j, col in enumerate(table.c_list):
            table.data[i][j] = compute_intersection_size(table.r_list[i], table.c_list[j])
    return table

def target_list():
    # stdin file list -> intersection report
    # python3 ./lib/file_sets.py file_sets.py <target_file> <column>

    parser = argparse.ArgumentParser(description='')

    parser.add_argument(
        '-t',
        '--target',
        help="Target file",
        required=True,
        type=str
    )
    args = vars(parser.parse_args())
    file_input = sys.stdin
    intersection_stats({args["target"]}, file_input)

def list_list_table():
    parser = argparse.ArgumentParser(description='')

    parser.add_argument(
        '-x',
        '--list_x',
        required=True,
        type=str
    )
    parser.add_argument(
        '-y',
        '--list_y',
        required=True,
        type=str
    )
    args = vars(parser.parse_args())

    r_list_filter = f"find ./rsc/ -type f | grep -P '{args['list_x']}'"
    c_list_filter = f"find ./rsc/ -type f | grep -P '{args['list_y']}'"

    r_list = subprocess.run(r_list_filter, shell=True, capture_output=True, text=True).stdout.splitlines()
    c_list = subprocess.run(c_list_filter, shell=True, capture_output=True, text=True).stdout.splitlines()

    print_header(c_list)
    intersection_stats(r_list, c_list).print()
if __name__ == "__main__":
   list_list_table()




