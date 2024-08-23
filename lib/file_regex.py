from pass_config import CONFIG
SEP = CONFIG['all']['separator']

# get regex from key
def get_regex(key) -> str | None:
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


def get_file_regex(filepath) -> str:
    return filepath.split('/')[-1].rstrip('\n').removesuffix('.txt').rstrip('\n')


#  file_path  -> regex
def file_regex_to_regex(file_path) -> str:
    regex = ""
    file_regex = get_file_regex(file_path)
    while file_regex != "":
        if get_regex(file_regex.split(SEP)[0]) is None:
            regex += SEP + file_regex.split(SEP)[0]
        else:
            regex += SEP + get_regex(file_regex.split(SEP)[0])
        file_regex = file_regex[len(file_regex.split(SEP)[0]):]
        file_regex = file_regex.lstrip(SEP)
    return regex.lstrip(SEP)


# Print list of file_regexes from file list to stdout
def print_file_regex(input_stream):
    for line in input_stream:
        print(file_regex_to_regex(line))

# get maximum file regex for all types in file list
def get_max_file_regex(file_list):
    unique_parts = set()
    for file_path in set(file_list):
        file_regex = get_file_regex(file_path)
        parts = file_regex.split(SEP)
        unique_parts.update(parts)
    sorted_parts = sorted(unique_parts)
    return SEP.join(sorted_parts)