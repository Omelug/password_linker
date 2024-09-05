import logging
import os
import sys, optparse, re, string
from string import ascii_uppercase

import input_parser

__author__ = 'Omelug'
__date__ = '2024'
__description__ = "Get often used sequences"
__external_tools__ = []

# I have stole code from jcchurch, thanks
__inpired_author__ = 'jcchurch'
__inpired_src__ = "https://github.com/jcchurch/Character-Frequency-CLI-Tool"


def get_args(args):
    parser = input_parser.InputParser()
    parser.add_argument('--window', '-w',help="sequence size (Default size=1)", default=1)
    parser.add_argument('--roll', '-r',
                   help="Rolling Window (Shift window by ROLL rather than WINDOW)", default=-1)
    parser.add_argument('--skipspaces', '-s', action="store_true", help="Skip Space Characters [ \\t\\r\\n]", default=False)
    parser.add_argument('--ascii_out', action="store_true", default=False)

    parser.add_argument('--in_file_list', type=str, default=None)
    parser.add_argument('--out_file', type=str, default=None)

    parsed_args, _ = parser.parse_known_args(args)
    return parsed_args

def charfreq(in_file_list=None,out_file=None, window=None, shift=-1, skipspaces=True, ascii_out=False):

    message = open(in_file_list, 'r').read() if isinstance(in_file_list, str) else sys.stdin.read()

    window = int(window)
    shift = window if shift == -1 else shift

    if skipspaces:
        message = re.sub(r"\s+", "", message)

    tokens = [message[i:i+window] for i in range(0, len(message) - window + 1, shift)]

    for (f, key) in frequency(tokens):
        printEntry(key, f, out_file, ascii_out=ascii_out)

def frequency(tokens):
    freq = {token: tokens.count(token) for token in set(tokens)}
    return sorted([(count, token) for token, count in freq.items()], key=lambda x: -x[0])

def printEntry(key, freq, out_file=None, ascii_out=False):
    out_file = open(out_file, 'w') if isinstance(out_file, str) else sys.stdout

    ordinals = '-'.join(str(ord(c)) for c in key)
    description = ''.join(
        "\\n" if c == "\n" else
        "\\t" if c == "\t" else
        "\\r" if c == "\r" else
        "\\s" if c == " " else
        c if c in string.printable else
        "?" for c in key
    )
    print(f"{freq}:", file=out_file, end='')
    if ascii_out:
        print(f"{ordinals}:", file=out_file,end='')
    print(f"{description}", file=out_file)

def run(args, config=None):
    script_name = os.path.basename(__file__)
    logging.info(f"--> {script_name}")
    ARGS = get_args(args)

    charfreq(in_file_list=ARGS.in_file_list,
            out_file=ARGS.out_file,
            window=ARGS.window,
            shift=ARGS.roll,
            skipspaces=ARGS.skipspaces,
            ascii_out=ARGS.ascii_out)


