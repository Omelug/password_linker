import os
import sys
import re

from lib.logfile import LogFile

lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.')
sys.path.append(lib_dir)
from lib.file_format import *
from lib.file_regex import *

LINKED_FOLDER = "./linkedLists"
PATCH_FILE = "./patch"

#  Control if in file stream has valid to regexes from file name
def control_file_regex(filepath, regex_pattern, patch=None) -> bool:
    filepath = filepath.strip('\n')
    try:
        regex = re.compile(regex_pattern)
        result = True
        with open(filepath, 'r') as file:
            line_number = 1
            for line in file:
                if not regex.match(line.strip()):
                    print(
                        f"{filepath} {line.strip()}   on line {line_number} \n does not match pattern: {regex_pattern}",
                        file=sys.stderr)
                    if patch is True:
                        # FIXME musi strip vymaze \n na konci,a le i mezery na zacatku, treba zmenit a vyzkouset i s posledni rakou
                        add_unique(PATCH_FILE, f"{filepath}\t'{regex_pattern}'\t{line.rstrip()}\t|")
                    result = False
                line_number += 1
        return result
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
    except re.error as e:
        print("Error compiling regular expression:", e)
    return False


#  control file list has valid to regexes from file name
def control_file_list_file_regex(input_stream, patch=None):
    for line in input_stream:
        regex = file_regex_to_regex(line)
        control_file_regex(line, '^' + regex + SEP + '?$', patch)


def link_column(file_list, out_file_r) -> None:
    """
    get value of key from stream and print them to stdout
    TODO unit  přes vice casti regexu promenych
    """

    log_file = LogFile(os.path.abspath(f"{LINKED_FOLDER}/linkedList.json"))
    unique_id = log_file.new(args=sys.argv)

    empty = 0
    err = set({})
    status = "succesful"

    for file_path in set(file_list):  # open file ,remove duplicates
        try:
            with open(file_path.rstrip('\n'), 'r') as file:
                for in_line in file:

                    keys = get_file_regex(file_path).split(SEP)
                    values = in_line.strip().split(SEP)
                    in_dict = dict(zip(keys, values))
                    out_dict = {key: "" for key in get_file_regex(out_file_r).split(SEP)}

                    try:
                        for out_key in get_file_regex(out_file_r).split(SEP):
                            if out_dict[out_key] != "":
                                logging.error(f"Rewrite error: {out_dict[out_key]}-->{in_dict[out_key]}")
                            out_dict[out_key] = in_dict[out_key]
                    except KeyError:
                        pass
                        #logging.error(f"Index Error: {file} {e} {index} {parts}")
                    print(SEP.join(list(out_dict.values())))
        except FileNotFoundError:
            logging.error(f" File '{file_path}' not found.")
            err.add(f"FileNotFoundError {file_path}")
        except ValueError as e:
            logging.error(f"ERROR: Value error {e}  {file_path}")
    log_file.update(unique_id, "stoptime", now_string())
    log_file.update(unique_id, ["progress", "status"], status)
    log_file.update(unique_id, ["progress", "errors"], list(err))

    logging.warning(f"ERROR: {empty} empty lines") if empty != 0 else None


def print_help():
    print(
        """
        --file_regex : transfer list (in stdin) of files to file_regex list 
        --control : check if each file in file list (in stdin) has valid file data (from his file_regex)
            -p for generate patch
        --link : link data from file list with file regex -> stdout
        """
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)
    if sys.argv[1] == "file_regex":
        print_file_regex(sys.stdin)
        sys.exit(0)
    if sys.argv[1] == "control":
        if (len(sys.argv) > 2) and (sys.argv[2] == "-p"):
            control_file_list_file_regex(sys.stdin, patch=True)
        control_file_list_file_regex(sys.stdin)
    if sys.argv[1] == "patch":
        #FIXME sed not working for texts with //
        with (open(PATCH_FILE, 'r') as patch_file):
            for line in patch_file:

                r = re.search(r"([^']*?'){2}\t(.*)\t\|(.*)", line)
                if r is None:
                    print("r is NOne", line)
                    continue
                old = r.group(2)
                new = r.group(3)

                path = re.search(r"(.*?)\t", line).group(1)
                if new != "" and new != " ":
                    # FIXME /DELETE nici, ale nechava prazdne radky
                    if "/DELETE" == new:
                        new = ""
                    command = ['sed', '-i', f"s/^{old}/{new}/m", f"{path}"]
                    print(' '.join(command))
                    subprocess.run(command, check=True)
    if sys.argv[1] == "link":
        if len(sys.argv) < 3:
            logging.critical("Use: python3 passlist.py <file_regex> < \"file list\"")
            #EXAMPLE  python3 passlist.py link pass < <(echo "rsc/...../email:pass.txt")
        else:
            link_column(sys.stdin, out_file_r=sys.argv[2])
