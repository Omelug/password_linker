import logging
import os
import subprocess
import sys
import input_parser

__author__ = 'Omelug'
__date__ = '2024'
__description__ = """Filter files by regex"""


REGEX_DICT = {
    "CZECH" : r'czech|databáze|česk|prague|praha|[^a-zA-Z]cz[^a-zA-Z]',
    "SLOVAK" : r'slovak|databáza|bratislav|[^a-zA-Z]sk[^a-zA-Z]',
    "EUROPE" : r'Europe|[^a-zA-Z]eu[^a-zA-Z]'
}

def print_help():
    print("""
        Usage:
            python3 filter.py 
                --regex_name <regex_name> < \"file list\
    """)

def get_args(args):
    parser = input_parser.InputParser(description="Linker Script")
    parser.add_argument("--regex_name", type=str, required=True)

    parser.add_argument('--in_file_list', type=str, default=None)

    parsed_args, _ = parser.parse_known_args(args)
    return parsed_args


def filter_file(file_path, regex):
    try:
        with subprocess.Popen(['grep', '-iP', regex, file_path], stdout=subprocess.PIPE, text=True) as proc:
            for line in proc.stdout:
                print(line, end='')
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found.")
    except IOError as e:
        logging.error(f"IO error: {e}")


def filter_lines(in_file_list, regex_name):
    """
    just filter file lines by regex
    """

    in_file_list = list(open(in_file_list, 'r')) if isinstance(in_file_list, str) else list(sys.stdin)

    regex = REGEX_DICT.get(regex_name)
    if regex is None:
        logging.error(f"Unknown regex name {regex_name}")
        return

    for file_path in {f.rstrip('\n') for f in set(in_file_list)}:
        try:
            filter_file(file_path, regex=regex)
        except FileNotFoundError:
            logging.error(f" File '{file_path}' not found.")
        except ValueError as e:
            logging.error(f"Value error {e} {file_path}")

def run(args, config=None):
    script_name = os.path.basename(__file__)
    logging.info(f"--> {script_name}")
    ARGS = get_args(args)

    filter_lines(ARGS.in_file_list, regex_name=ARGS.regex_name)

