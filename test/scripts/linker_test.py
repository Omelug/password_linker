import difflib
import json
import logging
import os
import subprocess
import filecmp
from colorama import Fore

logging.basicConfig(level=logging.ERROR)

DEBUG=True

DEFAULT_JSON = {
    "output":"output.txt",
    "command":"command.txt",
    "result":"result.txt",
    "data":"data",
    "cmd_prefix":"find"
}

def run_test(directory, check_order=False, sub_folder=".") -> bool:
    """
    default: data -> command.txt -> result.txt == output.txt?
    check config = result.json
    """

    #load result, override default values
    RESULT_JSON = DEFAULT_JSON.copy()
    result_json_path = os.path.join(directory, 'result.json')
    if os.path.exists(result_json_path):
        with open(result_json_path, 'r') as json_file:
            result_data = json.load(json_file)
            RESULT_JSON.update(result_data)

    output_file = os.path.join(directory, RESULT_JSON['output'])
    commands_file = os.path.join(directory, RESULT_JSON['command'])
    result_file = os.path.join(directory, RESULT_JSON['result'])

    # Check if all necessary files exist
    if not all(os.path.exists(f) for f in [output_file, commands_file]):
        print(f"Missing required files in {directory}")
        return False

    # Read the command from commands.txt
    with open(commands_file, 'r') as cmd_file:
        command = cmd_file.read().strip()

    #set up command changes
    if RESULT_JSON['cmd_prefix'] == 'find':
        command = f"find ./{sub_folder}/{os.path.basename(directory)}/{RESULT_JSON['data']}/ -type f | sort -t/ -k2,2| {command}"
    if RESULT_JSON['cmd_prefix'] == 'cat':
        command = f"cat ./{sub_folder}/{os.path.basename(directory)}/{RESULT_JSON['data']}/* | {command}"
    command = f"{command} > ./{sub_folder}/{os.path.basename(directory)}/{RESULT_JSON['result']}"

    print(Fore.CYAN, command, Fore.RESET)
    try:
        subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if check_order:
            comparison = filecmp.cmp(result_file, output_file, shallow=False)
        else:
            with open(result_file, 'r') as rf, open(output_file, 'r') as of:
                result_lines = sorted(rf.readlines())
                output_lines = sorted(of.readlines())
                comparison = result_lines == output_lines

        if comparison:
            print(Fore.GREEN + f"Test passed in {directory}")
            return True
        else:
            print(Fore.RED + f"Test failed in {directory}")
            if DEBUG:
                print(Fore.YELLOW + "Differences:")
                if check_order:
                    with open(result_file, 'r') as rf, open(output_file, 'r') as of:
                        result_lines = rf.readlines()
                        output_lines = of.readlines()
                for line in difflib.unified_diff(result_lines, output_lines, fromfile='result_file', tofile='output_file'):
                    print(line.rstrip())
            return False
    except subprocess.CalledProcessError:
        print(Fore.RED + f"Error running command in {directory}")
        return False


# Main function to iterate through all test directories
def main():
    base_dir = os.getcwd()
    passed, failed = 0, 0
    for sub_dir in [os.path.join(base_dir, entry) for entry in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, entry))]:
        for entry in os.listdir(sub_dir):
            full_path = os.path.join(sub_dir, entry)
            if os.path.isdir(full_path) and entry.startswith("test"):
                if run_test(full_path, check_order=False, sub_folder=os.path.basename(sub_dir)):
                    passed += 1
                else:
                    failed += 1

    print(Fore.CYAN, "\nResult:", Fore.GREEN, f"\tPassed {passed}/{passed+failed}", Fore.RED, f"\tFailed {failed}/{passed+failed}", Fore.RESET)

if __name__ == "__main__":
    main()