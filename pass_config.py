import json
import os
import sys

folder_path = os.path.dirname(os.path.abspath(__file__))
SECRET_FILE = f"pass_secret.py"

"""if not os.path.exists(SECRET_FILE):
    with open(SECRET_FILE, 'w+') as f:
        print("DATABASE_URL_ASYNC = 'postgresql+asyncpg://<database username>:<password>@localhost:5432/<db_name>'", file=f)
        print(f"Please, edit {SECRET_FILE}")
    exit(0)
else:
    from pass_secret import DATABASE_URL_ASYNC
"""

DEFAULT_CONFIG = {
        "all": {
            "separator": ":"
        },
        "pass_hub": {
            'patch_file':"./patch",
            'script_path':"./script"
        },
        "linker.py": {
            "linked_folder": "./linkedLists",
            'separator': ':'
        },
    }

global CONFIG

def generate_default():
    with open("config.json", 'w') as f:
        json.dump(CONFIG, f, indent=4)

def load_config(config_file="config.json"):
    global CONFIG
    CONFIG = DEFAULT_CONFIG.copy()
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            file_config = json.load(f)
        CONFIG.update(file_config)
load_config()

if __name__ == "__main__":
    if '--generate_default' in sys.argv:
        generate_default()
