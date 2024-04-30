import os
import sys
import re
import logging
from datetime import datetime

from colorama import init, Fore, Style
import json

SEP = ':'  # SEPARATOR
LINKED_FOLDER="../linkedLists" #linkedList Deafult #TODO

def help():
    print("TODO help")


def getregex(key) -> str | None:
    """
    Returns
    -------
    str
        regex for maching key or none if not exist
    Examples
    --------
    >>> getregex("salt")
    '.+?'
    >>> getregex("not known value") # check f return None
    """
    key_value_map = {
        "salt": ".+?",
        "hash": ".*?",
        "md5": ".{32}",
        "sha1": ".{40}",
        "pass": ".*?",
        "user": ".*?",
        "email": ".*?@.*?"
    }
    try:
        return key_value_map[key]
    except KeyError:
        return None


def check_file_with_regex(filepath, regex_pattern) -> bool:
    """

    """
    filepath = filepath.strip('\n')
    try:
        regex = re.compile(regex_pattern)
        with open(filepath, 'r') as file:
            line_number = 1
            for line in file:
                if not regex.match(line.strip()):
                    print(
                        f"{filepath} {line.strip()}   on line {line_number} \n does not match pattern: {regex_pattern}",
                        file=sys.stderr)
                    return False
                line_number += 1
        return True
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
    except re.error as e:
        print("Error compiling regular expression:", e)
    return False


def get_file_regex(filepath) -> str:
    """
    Returns
    -------
    str:
        regex of file, extracted from filenameExamples
    --------
    >>> get_file_regex("/home/kali/Desktop/JetBrains/PyCharm/passwordList/rsc/data/edited/dr7_users/md5:pass.txt")
    'md5:pass'
    >>> get_file_regex("/edited/dr7_users/test.txt")
    'test'
    >>> get_file_regex("nic_nemenit")
    'nic_nemenit'
    """
    return filepath.split('/')[-1].rstrip('\n').removesuffix('.txt')


def file_regex_to_regex(line):
    """
    Examples
    --------
    #TODO misto toho tady dat nejakou estu k testovacim datum
    >>> get_file_regex("/home/kali/Desktop/JetBrains/PyCharm/passwordList/rsc/data/edited/dr7_users/md5:pass.txt")
    '.*{}:.*'
    >>> get_file_regex("/edited/dr7_users/test:pass.txt")
    'test:.*'
    >>> get_file_regex("nic_nemenit")
    'nic_nemenit'
    """
    line = line.rstrip('\n')
    regex = ""
    file_regex = get_file_regex(line)
    logging.debug(line, " ", line.split('/')[-1].rstrip('\n').removesuffix(".txt"))  # TODO others formats
    while file_regex != "":
        if getregex(file_regex.split(SEP)[0]) is None:
            print(file_regex)
            logging.error(line.rstrip('\n'), "has not known key", file_regex.split(SEP)[0])
            file_regex = ""
            continue
        regex += SEP + getregex(file_regex.split(SEP)[0])
        file_regex = file_regex[len(file_regex.split(SEP)[0]):]  # TODO not only
        file_regex = file_regex.lstrip(SEP)
    return regex.lstrip(SEP)


def control_file_regex(input_stream):
    """
    Control if in file stream are valid regexes from file name
    #TODO do test with test data
    """
    for line in input_stream:
        regex = file_regex_to_regex(line)
        check_file_with_regex(line, '^' + regex + SEP + '?$')


def link_colmun(input_stream, key) -> None:
    """
    get value of key from stream and print them to stdout
    TODO dodelat linkovani přes vice casti regexu promenych
    """

    logging.debug("Linking from key {key}")
    empty = 0

    # zjistit jestli tam nejaky soubor neni vycrat, kdyztak zahlasit warning a amazat ho
    #zjistit kam ukladat linkedList.json, zalozit pokud neexistuje

    file_path = os.path.join(LINKED_FOLDER, "linkedList.json")

    data = {
        "start_time": datetime.now(),
        "input_args": sys.argv,
        "progress": {
            "status": "started",
            "errors": []
        }
    }

    with open(file_path, "w+") as outfile:
        json.dump(data, outfile, indent=4)

    #TODO open linkedList.json, add lined process with progress and start time
    # succesfull,, trvani, input args, tabulka pruniku,
    # nektere veci nedalat, pokud neni potraba

    for line in input_stream:
        line = line.rstrip('\n')
        try:
            index = get_file_regex(line).split(SEP).index(key)
            #zjednodujit pokud jde
            with open(line, 'r') as file:
                for line2 in file:
                    parts = line2.strip().split(SEP)
                    if parts[index] == "":
                        empty += 1
                    else:
                        print(parts[index])
        except IndexError:
            logging.error(f"Index Error: {file}")
        except FileNotFoundError:
            #save error
            logging.error(f" File '{line}' not found.")
        except ValueError as e:
            logging.error(f"ERROR: Value error {e}  {line}")
    #zapsat do jsonu dokonceno, zapsat cas
    logging.warning(f"ERROR: {empty} empty lines")


def file_regex(input_stream):
    """
    Print list of file_regexes from file list to stdout
    >>> file_regex(["pass:sha1.txt","pass:md5.txt"])
    .*?:.{40}
    .*?:.{32}
    """
    for line in input_stream:
        print(file_regex_to_regex(line))

import argparse
if __name__ == "__main__":
    """
        --file_regex tranfer list (in stdin) of files to file_regex list 
        --control check if each file in file list (in stdin) has valid for file data (from his file_regex)
        --link link data from file list with file regex -> stdout
    """

    if len(sys.argv) < 2:
        help()
        sys.exit(0)
    if sys.argv[1] == "file_regex":
        file_regex(sys.stdin)
        sys.exit(0)
    if sys.argv[1] == "control":
        control_file_regex(sys.stdin)
    if sys.argv[1] == "link":
        if len(sys.argv) < 3 or getregex(sys.argv[2]) is None:
            logging.critical("Use: python3 passlist.py <file_regex> < \"file list\"")
            #EXAMPLE  python3 passlist.py link pass < <(echo "rsc/...../email:pass.txt")
        else:
            link_colmun(sys.stdin, sys.argv[2])
