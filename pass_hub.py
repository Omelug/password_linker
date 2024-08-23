import importlib.util
import os
import sys
import re
from lib.logfile import LogFile

lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.')
sys.path.append(lib_dir)
from lib.file_format import *
from lib.file_regex import *
from pass_config import CONFIG
conf = CONFIG['pass_hub']

logging.basicConfig(level=logging.INFO)

#  Control if in file stream has valid to regexes from file name
def control_file_regex(filepath, regex_pattern, patch=None) -> bool:
    filepath = filepath.strip('\n')
    try:
        regex = re.compile(regex_pattern)
        result = True
        with open(filepath, 'r') as file:
            line_number = 1
            for line in file:
                if not regex.match(line.strip()):
                    print(
                        f"{filepath} {line.strip()}   on line {line_number} \n does not match pattern: {regex_pattern}",
                        file=sys.stderr)
                    if patch is True:
                        # FIXME musi strip vymaze \n na konci,ale i mezery na zacatku, treba zmenit a vyzkouset i s posledni rakou
                        add_unique(conf['patch_file'], f"{filepath}\t'{regex_pattern}'\t{line.rstrip()}\t|")
                    result = False
                line_number += 1
        return result
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
    except re.error as e:
        print("Error compiling regular expression:", e)
    return False


#  control file list has valid to regexes from file name
def control_file_list_file_regex(input_stream, patch=None):
    for line in input_stream:
        regex = file_regex_to_regex(line)
        control_file_regex(line, '^' + regex + SEP + '?$', patch)


def print_help():
    print(
        """
        python3 pass_hub.py <script> <args>
        
        stdin -> stdout 
        
        Base scripts
        link - link lists
        merer - merge list, remove duplicates
        mask - find masks for list
        """, file=sys.stderr
    )


def print_e(msg):
    print(msg, file=sys.stderr)

def find_script_path(script_name):
    script_base_path = os.path.abspath(os.path.dirname(__file__))
    base_path = os.path.join(script_base_path, conf['script_path'])
    find_cmd = subprocess.run(['find', base_path, '-name', f"{script_name}"], capture_output=True, text=True)
    matches = find_cmd.stdout.strip().split('\n')
    logging.debug(f"{find_cmd} --> {matches}")
    if len(matches) == 0 or matches == ['']:
        raise FileNotFoundError(f"No script named '{script_name}' found in '{base_path}'")
    elif len(matches) > 1:
        raise ValueError(f"Multiple scripts named '{script_name}' found in '{base_path}': {matches}")
    return matches[0]

def import_script(script_path):
    spec = importlib.util.spec_from_file_location("imported_script", script_path)
    imported_script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(imported_script)
    return imported_script

if __name__ == "__main__":
    if sys.argv[1] == "help" or sys.argv[1] is None:
        print_help()
    else:
        script_path = find_script_path(sys.argv[1])
        imported_script = import_script(script_path)
        run_func = getattr(imported_script, 'run')
        run_func(args=sys.argv,config=CONFIG)
"""
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)
    if sys.argv[1] == "file_regex":
        print_file_regex(sys.stdin)
        sys.exit(0)
    if sys.argv[1] == "control":
        if (len(sys.argv) > 2) and (sys.argv[2] == "-p"):
            control_file_list_file_regex(sys.stdin, patch=True)
        control_file_list_file_regex(sys.stdin)
    if sys.argv[1] == "patch":
        #FIXME sed not working for texts with //
        with (open(conf['patch_file'], 'r') as patch_file):
            for line in patch_file:

                r = re.search(r"([^']*?'){2}\t(.*)\t\|(.*)", line)
                if r is None:
                    print("r is NOne", line)
                    continue
                old = r.group(2)
                new = r.group(3)

                path = re.search(r"(.*?)\t", line).group(1)
                if new != "" and new != " ":
                    # FIXME /DELETE nici, ale nechava prazdne radky
                    if "/DELETE" == new:
                        new = ""
                    command = ['sed', '-i', f"s/^{old}/{new}/m", f"{path}"]
                    print(' '.join(command))
                    subprocess.run(command, check=True)
    if sys.argv[1] == "link":
        if len(sys.argv) < 3:
            logging.critical("Use: python3 pass_hub.py <file_regex> < \"file list\"")
        else:
            link_column(sys.stdin, out_file_r=sys.argv[2])
            
            """
