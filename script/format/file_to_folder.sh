#!/bin/bash

#TODO unit test
# Loop through each file in the current directory
for file in *; do
    # Check if the item is a file (not a directory)
    if [[ -f "$file" ]]; then
        # Extract the filename without extension
        filename=$(basename -- "$file")
        filename_no_ext="${filename%.*}"

        # Create a folder with the same name as the file (if not already exist)
        mkdir -p "$filename_no_ext"

        # Move the file into the folder
        mv "$file" "$filename_no_ext/"

        echo "Moved $file to $filename_no_ext/"
    fi
done
