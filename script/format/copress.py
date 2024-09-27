import logging
import os
import argparse

__author__ = 'Omelug'
__date__ = '2024'
__description__ = "Compress file list content into stdout"

CONFIG= {}
conf = {}

logging.basicConfig(level=logging.INFO)

def get_args(args):
    parser = argparse.ArgumentParser(description="Compress Script")
    parsed_args, _ = parser.parse_known_args(args)
    return parsed_args

def run(args, config=None):
    script_name = os.path.basename(__file__)
    logging.info(f"Runned {script_name}")
    global conf
    global CONFIG
    CONFIG=config
    conf = CONFIG.get(script_name)
    ARGS = get_args(args)
    #TODO implement compress function
    #compress(out_regex=ARGS.file_regex, out_file=ARGS.out_file)


