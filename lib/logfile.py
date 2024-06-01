# Log list logffile.py
# for logffile
import json
import logging
import uuid
import os
import sys
lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../lib')
sys.path.append(lib_dir)
import file_format
import os


class LogFile:
    def __init__(self, path):
        self.path = path
        if os.path.isdir(self.path):
            raise IsADirectoryError
        if not os.path.isabs(self.path):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.path = os.path.abspath(os.path.join(current_dir, path))
        if not self.path.endswith('.json'):
            logging.error("Path have to be json")
            exit(1)
        file_format.create_empty_json(self.path)
        logging.debug(f"Init of LogFile for {self.path}")

    def new(self, args, uuid_strict=None) -> uuid.UUID | None:
        try:
            with open(self.path, "r") as json_file:
                existing_data = json.load(json_file)
        except FileNotFoundError:
            existing_data = []
        if uuid_strict is None:
            unique_id = str(uuid.uuid4())
        else:
            unique_id = uuid_strict
        new_item = {
            "uuid": unique_id,
            "start_time": file_format.now_string(),
            "input_args": args,
            "progress": {
                "status": "started",
                "errors": []
            }
        }
        #FIXme proc to nekdy vraci dict anekdy list ?
        if isinstance(existing_data, dict):
            existing_data = list(existing_data.values())
        if isinstance(existing_data, list):
            existing_data.append(new_item)
        with open(self.path, "w+") as log_file:
            json.dump(existing_data, log_file, indent=42)
        return unique_id

    def __add__(self, other):
        #TODO merge log files
        pass

    def __sub__(self, other):
        #TODO
        pass

    def get_or_none(self, it_uuid):
        with open(self.path, 'r') as json_file:
            data = json.load(json_file)
        for item in data:
            if item.get('uuid') == str(it_uuid):
                return item
        return None

    def get_or_create(self,it_uuid):
        item = self.get_or_none(it_uuid)
        if item is None:
            self.new([], uuid_strict=it_uuid)
            item = self.get_or_none(it_uuid)
        return item
    def stats(self):
        #TODO get item count, stats about error etc.
        pass

    def add_to_list(self, it_uuid, key, value):
        with open(self.path, 'r') as json_file:
            data = json.load(json_file)
        for item in data:
            if item.get('it_uuid') == it_uuid:
                item[key] = value
                break
        else:
            logging.error(f"Item with it_uuid {it_uuid} not found")
            return -1
        with open(self.path, 'w') as json_file:
            json.dump(data, json_file)
        logging.debug("In ", self.path, f" added {key}:{value} to {it_uuid}")

    def update(self, it_uuid, key, value) -> bool:
        with open(self.path, 'r') as json_file:
            data = json.load(json_file)
        for item in data:
            if item.get('uuid') == str(it_uuid):
                if isinstance(key, list):
                    nested_item = item
                    for k in key[:-1]:
                        nested_item = nested_item.setdefault(k, {})
                    nested_item[key[-1]] = value
                else:
                    item[key] = value
                break
        else:
            logging.error(f"Item with it_uuid {it_uuid} not found")
            return False
        with open(self.path, 'w+') as json_file:
            json.dump(data, json_file)
        logging.debug("In ", self.path, f" updated value {key} to {value} in {it_uuid}")
        return True

    def add_error(self, it_uuid, e):
        return add_to_list(it_uuid, "error", e.__name__)

    def add_error_msg(self, it_uuid, msg):
        return add_to_list(it_uuid, "error", msg)
