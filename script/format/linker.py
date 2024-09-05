import logging
import os
import sys
import input_parser
from lib.file_regex import get_file_regex, get_max_file_regex

__author__ = 'Omelug'
__date__ = '2024'
__description__ = "Link files to one file"


CONFIG= {}
conf = {}

logging.basicConfig(level=logging.ERROR)

def print_file_values(file_path, out_keys, SEP=None,out_file=None) -> None:
    try:
        with open(file_path.rstrip('\n'), 'r') as file:
            keys = get_file_regex(file_path).split(SEP)  # get keys from file name
            out_dict_tem = {key: "" for key in out_keys}
            for in_line in file:
                values = in_line.strip().split(SEP)
                in_dict = dict(zip(keys, values))
                out_dict = out_dict_tem.copy()

                for out_key in out_keys:
                    if out_dict[out_key] != "":
                        logging.error(f"Rewrite error: {out_dict[out_key]}-->{in_dict[out_key]}")
                    out_dict[out_key] = in_dict.get(out_key, "")

                # logging.error(f"Index Error: {file} {e} {index} {parts}")
                print(SEP.join(out_dict[key] for key in out_keys), file=out_file)
    except IsADirectoryError:
        logging.error(f"Is a directory: {file_path}")


def link_column(in_file_list=None, out_regex=None,out_file=None) -> None:
    """
    cut off everything get value of key from stdout and print them to stdout
    :param in_file_list: list of files, where are files are unique (if not reduced to set)
    :param out_regex: file regex of output file
    :param out_file: output file, default stdout
    """
    #first set up default values, if not set

    in_file_list = list(open(in_file_list, 'r')) if isinstance(in_file_list, str) else list(sys.stdin)
    out_file = open(out_file, 'w') if isinstance(out_file, str) else sys.stdout

    if out_regex is None: # no output regex, maximalize output regex
        out_regex = get_max_file_regex(in_file_list)


    logging.info(f"Linking files to regex {out_regex}")
    #---------------------------------------------

    #log_file = LogFile(os.path.abspath(f"{conf['linked_folder']}/linkedList.json"))
    #unique_id = log_file.new(args=sys.argv)

    empty = 0
    err = set()
    SEP = conf['separator']
    out_keys = get_file_regex(out_regex).split(SEP)

    #print_e(in_file_list)
    #print_e(out_regex)
    for file_path in {f.rstrip('\n') for f in set(in_file_list)}:  # open file ,remove duplicates
        #print_e(file_path)
        try:
            print_file_values(file_path, out_keys=out_keys,SEP=SEP, out_file=out_file)
        except FileNotFoundError:
            logging.error(f" File '{file_path}' not found.")
            err.add(f"FileNotFoundError {file_path}")
        except ValueError as e:
            logging.error(f"Value error {e} {file_path}")
    #log_file.update(unique_id, "stoptime", now_string())
    #log_file.update(unique_id, ["progress", "status"], status)
    #log_file.update(unique_id, ["progress", "errors"], list(err))

    #print_e(f"Output is in format {out_regex}")
    logging.warning(f"ERROR: {empty} empty lines") if empty != 0 else None

def print_help():
    print("""
        Usage:
            python3 pass_hub.py linker 
                --file_regex <file_regex> < \"file list\
                --control : check if each file in file list (in stdin) has valid file data (from his file_regex)
                -p for generate patch
                --link : link data from file list with file regex -> stdout
    """)

def get_args(args):
    parser = input_parser.InputParser()
    parser.add_argument("--file_regex", type=str, required=True)

    parser.add_argument('--in_file_list', type=str, default=None)
    parser.add_argument('--out_file', type=str, default=None)

    parsed_args, _ = parser.parse_known_args(args)
    return parsed_args

def run(args, config=None):
    script_name = os.path.basename(__file__)
    logging.info(f"--> {script_name}")
    global conf
    global CONFIG
    CONFIG=config
    conf = CONFIG.get(script_name)
    ARGS = get_args(args)

    link_column(ARGS.in_file_list, out_regex=ARGS.file_regex, out_file=ARGS.out_file)

