import logging
import sys

import input_parser
import importlib.util
import string
import os
from collections import Counter

__author__ = 'Omelug'
__date__ = '2024'
__description__ = "Get mask from pass file"
__external_tools__ = []

# I have stole code from Password-Scripts
__inpired_author__ = 'Jake Miller (@LaconicWolf)'
__inpired_src__ = "https://github.com/laconicwolf/Password-Scripts"

ARGS = None
def print_help():
    # TODO --password "password"

    print("""
        Usage:
            python3 mask.py 
                --pass_list <regex_name> 
    """)

def get_args(args):
    parser = input_parser.InputParser()
    parser.add_argument("--pass_list", type=str, required=True)
    parser.add_argument("-v", "--verbose",action='store_true', help="Increase output verbosity.")
    #parser.add_argument("--password", type=str, required=True)
    parser.add_argument('--in_file_list', type=str, default=None)
    parser.add_argument('--out_file', type=str, default=None)

    parsed_args, _ = parser.parse_known_args(args)
    return parsed_args

def run(args, config=None):
    script_name = os.path.basename(__file__)
    logging.info(f"--> {script_name}")
    global ARGS
    ARGS = get_args(args)
    #import_tools()
    get_masks(in_file_list=ARGS.in_file_list, out_file=ARGS.out_file)

def generate_char_mask(word):
    """Generates mask for a word and returns the mask as a string."""
    mask = ''
    for char in word:
        if char in string.ascii_uppercase:
            mask += '?u'
        elif char in string.ascii_lowercase:
            mask += '?l'
        elif char in string.digits:
            mask += '?d'
        elif char in string.punctuation or char == ' ':
            mask += '?s'
        else:
            if ARGS.verbose:
                logging.warning(f'Encountered a non-standard character: {char}. It will appear in a mask as ?X')
            mask += '?X'
    return mask

def sort_char_masks(mask_list):
    """
    :return: sorted list of tuples [(mask, count)], Example: [('?l?l?l?l?l', 4)]
    """
    mask_dict = Counter(mask_list)
    return sorted(mask_dict.items(), key=lambda x: x[1], reverse=True)



def get_masks(in_file_list=None, out_file=None):
    """File list is converted to mask list sorted by count"""

    in_file_list = list(open(in_file_list, 'r')) if isinstance(in_file_list, str) else list(sys.stdin)
    out_file = open(out_file, 'w') if isinstance(out_file, str) else sys.stdout

    file_mask_list = []
    for filename in in_file_list:
        with open(filename.rstrip('\n'), encoding="utf8") as f:
            words = f.read().splitlines()

        # Generate the masks for each word and sort them by count.
        masks = [generate_char_mask(word) for word in words]
        file_mask_list.append(dict(sort_char_masks(masks))) # creating [{"mask":count, ...}, ...]

    # Gets all the unique masks
    mask_keys = set(k for d in file_mask_list for k in d.keys())

    # sum mask count from variout files
    results = {k: sum(d.get(k, 0) for d in file_mask_list) for k in mask_keys}

    # Sorts the tuples first by length, then by count
    sorted_results = sorted(results.items(), key=lambda x: (len(x[0]), -x[1]))

    for mask, count in sorted_results:
        print(f"{mask}:{count}", file=out_file)