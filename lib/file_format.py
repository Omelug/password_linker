import logging
import os
import json
import datetime
import time

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
            exit(f"File {file} not wasnt created")


def load_config(config_file_path: str, key: str, default: str) -> int | None:
    """
    exit if creation failed or not in JSON format
    """
    if create_file_if_not_exists(config_file_path):  #create empty but valid json
        config = {}
        with open(config_file_path, 'w') as config_file:
            json.dump(config, config_file)

    try:
        with open(config_file_path, "r") as config_file:
            config = json.load(config_file)
            return config.get(key, default)
    except FileNotFoundError:
        logging.critical(f"File {config_file_path} not found")
    except json.JSONDecodeError:
        logging.critical("Invalid JSON format in config file:", config_file_path)


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
