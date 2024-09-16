import argparse
import logging
import os
import sys, re, string
from lib import io_tubes

__author__ = 'Omelug'
__date__ = '2024'
__description__ = "Get often used sequences"
__external_tools__ = []

# I have stole code from jcchurch, thanks
__inpired_author__ = 'jcchurch'
__inpired_src__ = "https://github.com/jcchurch/Character-Frequency-CLI-Tool"


__in_format__ = {"REG_FILE_LIST": True}
__out_format__ = {"TXT_LIST": True}

def get_args(args):
    parser = argparse.ArgumentParser()
    io_tubes.parse(parser, __in_format__, __out_format__)
    parser.add_argument('--window', '-w',help="sequence size (Default size=1)", default=1)
    parser.add_argument('--roll', '-r',
                   help="Rolling Window (Shift window by ROLL rather than WINDOW)", default=-1)
    parser.add_argument('--skipspaces', '-s', action="store_true", help="Skip Space Characters [ \\t\\r\\n]", default=False)
    parser.add_argument('--ascii_out', action="store_true", default=False)

    return parser.parse_args(args)

def charfreq(window=None, shift=-1, skipspaces=True, ascii_out=False):

    message = sys.stdin.read()

    window = int(window)
    shift = window if shift == -1 else shift

    if skipspaces:
        message = re.sub(r"\s+", "", message)

    tokens = [message[i:i+window] for i in range(0, len(message) - window + 1, shift)]

    for (f, key) in frequency(tokens):
        printEntry(key, f, ascii_out=ascii_out)

def frequency(tokens):
    freq = {token: tokens.count(token) for token in set(tokens)}
    return sorted([(count, token) for token, count in freq.items()], key=lambda x: -x[0])

def printEntry(key, freq, ascii_out=False):

    ordinals = '-'.join(str(ord(c)) for c in key)
    description = ''.join(
        "\\n" if c == "\n" else
        "\\t" if c == "\t" else
        "\\r" if c == "\r" else
        "\\s" if c == " " else
        c if c in string.printable else
        "?" for c in key
    )
    print(f"{freq}:", end='')
    if ascii_out:
        print(f"{ordinals}:",end='')
    print(f"{description}")

def run(args, config=None):
    script_name = os.path.basename(__file__)
    logging.info(f"--> {script_name}")
    ARGS = get_args(args[2:])

    charfreq(window=ARGS.window,
            shift=ARGS.roll,
            skipspaces=ARGS.skipspaces,
            ascii_out=ARGS.ascii_out)


