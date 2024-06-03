import logging
import json
import datetime
import subprocess
import time

"""
Errors are not propagate up, all exit here (is important save consistent status before calling these function)
"""

def create_file_if_not_exists(file: str) -> int: #created? if error, exit(1)
    try:
        with open(file, 'r'):
            return False
    except FileNotFoundError:
        try:
            with open(file, 'a'):
                logging.info(f"File '{file}' created successfully.")
            return True
        except OSError as e:
            logging.critical(f"File {file} not wasn't created {e}")
            exit(1)


def create_empty_json(config_file_path, list=False): # True or exit
    if create_file_if_not_exists(config_file_path):
        config = {}
        if list:
            config = []
        try:
            with open(config_file_path, 'w') as config_file:
                json.dump(config, config_file)
            return True
        except OSError:
            logging.critical(f"New empty JSON {config_file_path} cant be opened")
            exit(1)
    return False

def load_config(config_file_path: str, key: str, default: str) -> int: # JSON config value, if error exit(1)
    create_empty_json(config_file_path)

    try:
        with open(config_file_path, "r") as config_file:
            config = json.load(config_file)
            return config.get(key, default)
    except FileNotFoundError:
        logging.critical(f"File {config_file_path} not found")
        exit(1)
    except json.JSONDecodeError:
        logging.critical("Invalid JSON format in config file:", config_file_path)
        exit(1)

# update or create kay
def update_config(config_file_path: str, key: str, new_value: str): # True if saved, False if error

    if create_file_if_not_exists(config_file_path):
        config_data = {}
    else:
        with open(config_file_path, 'r') as config_file:
            config_data = json.load(config_file)
    config_data[key] = new_value
    with open(config_file_path, 'w') as json_file:
        json.dump(config_data, json_file, indent=4)

def now_string():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def date_to_string(f_date: float):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(f_date))

#TODO unit test
def download_with_wget(url, output_directory):
    try:
        subprocess.run(['wget', '-O', output_directory, url], check=True)
        logging.info(f"{url} downloaded successful!")
        return True #FIXME for testing, return True
    except Exception as e:
        logging.error("Error downloading file:", e)
        return False

def print_json_file(file_path):
    try:
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
            print(json.dumps(data, indent=4))
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found")

def add_unique(file_name, needle) -> bool: #appended?
    create_file_if_not_exists(file_name)
    with open(file_name, 'r+') as file:
        for line in file:
            if needle in line:
                return False
        file.write(f"{needle}\n")
        return True
