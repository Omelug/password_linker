import argparse
import logging
import os
import subprocess
import sys
import lib.io_tubes as io_tubes

__author__ = 'Omelug'
__date__ = '2024'
__description__ = """Filter files by regex"""

__in_format__ = {"TXT_LIST": True, "REG_FILE_LIST": "TXT_LIST"}
__out_format__ = {"TXT_LIST": True}

REGEX_DICT = {
    "CZECH" : r'czech|databáze|česk|prague|praha|[^a-zA-Z]cz[^a-zA-Z]',
    "SLOVAK" : r'slovak|databáza|bratislav|[^a-zA-Z]sk[^a-zA-Z]',
    "EUROPE" : r'Europe|[^a-zA-Z]eu[^a-zA-Z]',
    "ASCII_ONLY" : r'^[\x00-\x7F]+$',
    "PLAIN_TEXT" : r'^[\x21-\x7E]+$'
}

def get_args(args):
    parser = argparse.ArgumentParser()
    io_tubes.parse(parser, __in_format__, __out_format__)
    parser.add_argument("--regex_name", type=str, required=True)
    return parser.parse_args(args)


def filter_file(file_path, regex):
    try:
        cmd = ['grep', '-iP', regex]
        if file_path:
            cmd.append(file_path)
        with subprocess.Popen(cmd,
                              stdin=sys.stdin if not file_path else None,
                              stdout=subprocess.PIPE,text=True) as proc:
            for line in proc.stdout:
                print(line, end='')
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found.")
    except IOError as e:
        logging.error(f"IO error: {e}")

def get_regex(regex_name):
    regex = REGEX_DICT.get(regex_name)
    if regex is None:
        logging.critical(f"Unknown regex name {regex_name}")
        sys.exit(1)
    return regex

def filter_file_list(regex_name):
    """
    filter every file on list
    """

    in_file_list = list(sys.stdin)
    regex = get_regex(regex_name)
    for file_path in {f.rstrip('\n') for f in in_file_list}:
        try:
            filter_file(file_path, regex=regex)
        except FileNotFoundError:
            logging.error(f" File '{file_path}' not found.")
        except ValueError as e:
            logging.error(f"Value error {e} {file_path}")

def run(args, config=None):
    script_name = os.path.basename(__file__)
    logging.info(f"--> {script_name}")
    ARGS = get_args(args[2:])

    if ARGS.in_format == "REG_FILE_LIST":
        filter_file_list(regex_name=ARGS.regex_name)
    if ARGS.in_format == "TXT_LIST":
        filter_file(None, regex=get_regex(ARGS.regex_name))


