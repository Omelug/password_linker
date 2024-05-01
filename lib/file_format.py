import logging
import os
import json
import datetime
import subprocess
import time
"""
Errors are not propagaded up, all stops here (is important save consistent status before calling these function)
"""
def create_file_if_not_exists(file: str) -> int:
    """
    @return 1 if created, 0 if already existed, -1 if error
    """
    try:
        with open(file, 'r'):
            return 0
    except FileNotFoundError:
        try:
            with open(file, 'w'):
                logging.info(f"File '{file}' created successfully.")
            return 1
        except FileNotFoundError:
            logging.critical(f"File {file} not wasnt created")
            exit(1)


def create_empty_json(config_file_path):
    if create_file_if_not_exists(config_file_path):
        config = {}
        try:
            with open(config_file_path, 'w') as config_file:
                json.dump(config, config_file)
            return 1
        except OSError:
            logging.critical(f"New empty JSON {config_file_path} cant be opened")
            exit(1)

def load_config(config_file_path: str, key: str, default: str) -> int | None:
    """
    exit if creation failed or not in JSON format
    """
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


def update_config(config_file_path: str, key: str, new_value: str):
    """
        @return 1 if saved, False if error
    """
    if create_file_if_not_exists(config_file_path):
        config_data = {}
    else:
        with open(config_file_path, 'r') as config_file:
            config_data = json.load(config_file)
    try:
        config_data[key] = new_value
        with open(config_file_path, 'w') as json_file:
            json.dump(config_data, json_file, indent=4)
        return True
    except ValueError:
        logging.error(f"Invalid value {new_value} for key {key}")
        return False


def now_string():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def date_to_string(f_date: float):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(f_date))

#TODO unit test
def download_with_wget(url, output_directory):
    """
    1 backup remove old downloaded file
    TODO asi nezalohovat nic
    """
    try:
        subprocess.run(['wget', url, '--backups=1 -P', output_directory], check=True)
        logging.info(f"{url} downloaded successful!")
        return True
    except Exception as e:
        logging.error("Error downloading file:", e)
        return False
