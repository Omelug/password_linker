import sys
import os
if __name__ == "__main__":
    import subprocess

    # Define the shell command
    command = "history | tail -n 2 | head -n 1"

    # Execute the command and capture its output
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        pipeline_command = result.stdout.strip()
        print("Pipeline command:", pipeline_command)
    else:
        # Print an error message if the command failed
        print("Failed to execute the command:", result.stderr)
