import argparse
import logging
import os
import sys

from lib import io_tubes
from lib.file_regex import get_file_regex, get_max_file_regex

__author__ = 'Omelug'
__date__ = '2024'
__description__ = "Link files to one file"

__in_format__ = {"REG_FILE_LIST": True}
__out_format__ = {"TXT_LIST": True}

CONFIG= {}
conf = {}

logging.basicConfig(level=logging.ERROR)

def print_file_values(file_path, out_keys, err=None) -> None:
    try:
        input_stream = sys.stdin if file_path is None else open(file_path.rstrip('\n'), 'r')
        with input_stream as file:
            keys = get_file_regex(file_path).split(conf['separator'])  # get keys from file name
            out_dict_tem = {key: "" for key in out_keys}
            for in_line in file:
                values = in_line.strip().split(conf['separator'])
                in_dict = dict(zip(keys, values))
                out_dict = out_dict_tem.copy()

                for out_key in out_keys:
                    if out_dict[out_key] != "":
                        logging.error(f"Rewrite error: {out_dict[out_key]}-->{in_dict[out_key]}")
                    out_dict[out_key] = in_dict.get(out_key, "")

                print(conf['separator'].join(out_dict[key] for key in out_keys))
    except IsADirectoryError:
        logging.error(f"Is a directory: {file_path}")
    except FileNotFoundError:
        logging.error(f" File '{file_path}' not found.")
        err.add(f"FileNotFoundError {file_path}") if err is not None else None
    except ValueError as e:
        logging.error(f"Value error {e} {file_path}")


def link_column(out_regex=None) -> None:
    """
    cut off everything get value of key from stdout and print them to stdout
    :param in_file_list: list of files, where are files are unique (if not reduced to set)
    :param out_regex: file regex of output file
    """
    #first set up default values, if not set

    in_file_list = list(sys.stdin)

    if out_regex is None: # no output regex, maximalize output regex
        out_regex = get_max_file_regex(in_file_list.copy())

    logging.info(f"Linking files to regex {out_regex}")

    empty = 0
    err = set()
    out_keys = get_file_regex(out_regex).split(conf['separator'])

    for file_path in {f.rstrip('\n') for f in set(in_file_list)}:  # open file ,remove duplicates
        print_file_values(file_path, out_keys=out_keys, err=err)

    logging.warning(f"ERROR: {empty} empty lines") if empty != 0 else None

def get_args(args):
    parser = argparse.ArgumentParser()
    io_tubes.parse(parser, __in_format__, __out_format__)
    parser.add_argument("--file_regex", type=str,
                        help="Output list in out_file_regex, default maximal")
    return parser.parse_args(args)

def run(args, config=None):
    script_name = os.path.basename(__file__)
    logging.info(f"--> {script_name}")
    global conf
    global CONFIG
    CONFIG=config
    conf = CONFIG.get(script_name)
    ARGS = get_args(args[2:])

    if ARGS.in_format == "REG_FILE_LIST":
        link_column(out_regex=ARGS.file_regex)