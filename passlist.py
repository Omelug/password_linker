import sys
import re

SEP = ':'  # SEPARATOR
DEBUG = 1

def help():
    print("TODO help")


def getregex(key):
    key_value_map = {
        "salt": ".+?",
        "hash": ".*?",
        "md5": ".{32}",
        "sha1": ".{40}",
        "pass": ".*?",
        "user": ".*?"
    }
    try:
        return key_value_map[key]
    except KeyError:
        return None


def check_file_with_regex(filepath, regex_pattern):
    filepath = filepath.strip('\n')
    try:
        regex = re.compile(regex_pattern)
        with open(filepath, 'r') as file:
            line_number = 1
            for line in file:
                if not regex.match(line.strip()):
                    print(f"{filepath} {line.strip()}   on line {line_number} \n does not match pattern: {regex_pattern}", file=sys.stderr)
                    return False
                line_number += 1
        return True
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        return False
    except re.error as e:
        print("Error compiling regular expression:", e)
        return False

def get_file_regex(filepath):
    return filepath.split('/')[-1].rstrip('\n').removesuffix('.txt')


def file_regex_to_regex(line):
    line = line.rstrip('\n')
    regex = ""
    file_regex = get_file_regex(line)
    if DEBUG:
        print(line, " ", line.split('/')[-1].rstrip('\n').removesuffix(".txt"), file=sys.stderr)  # TODO others formats
    while file_regex != "":
        if getregex(file_regex.split(SEP)[0]) is None:
            print(file_regex)
            print(line.rstrip('\n'), "has not known key", file_regex.split(SEP)[0], file=sys.stderr)
            file_regex = ""
            continue
        regex += SEP + getregex(file_regex.split(SEP)[0])
        file_regex = file_regex[len(file_regex.split(SEP)[0]):]  # TODO not only
        file_regex = file_regex.lstrip(SEP)
    return regex.lstrip(SEP)


def control_file_regex(input_stream):
    for line in input_stream:
        regex = file_regex_to_regex(line)
        check_file_with_regex(line, '^' + regex + SEP + '?$')


def link_colmun(input_stream, key):
    #print(key)
    empty = 0
    for line in input_stream:
        line = line.rstrip('\n')
        keys_list = get_file_regex(line).split(SEP)
        try:
            index = keys_list.index(key)
            try:
                with open(line, 'r') as file:
                    for line2 in file:
                        parts = line2.strip().split(':')
                        if parts[index] == "":
                            empty = empty + 1
                        else:
                            print(parts[index])
            except FileNotFoundError:
                print(f"Error: File '{line}' not found.")
        except ValueError as e:
            if DEBUG:
                print(f"ERROR: Value error ", e," ", line, file=sys.stderr)
            continue
    print(f"ERROR: {empty} empty lines ", file=sys.stderr)


def file_regex(input_stream):
    for line in input_stream:
        print(file_regex_to_regex(line))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        help()
    if sys.argv[1] == "file_regex":
        file_regex(sys.stdin)
    if sys.argv[1] == "control":
        control_file_regex(sys.stdin)
    if sys.argv[1] == "link":
        if len(sys.argv) < 3 or getregex(sys.argv[2]) is None:
            print("link key not valid", file=sys.stderr)
        else:
            link_colmun(sys.stdin, sys.argv[2])