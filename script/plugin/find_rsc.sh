#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <pwd>"
    exit 1
fi

while [ "$current_dir" != "passwordList" ]; do
    rsc_dir="$current_dir/rsc"
    if [ -d "$rsc_dir" ]; then
        echo "Found 'rsc' directory: $rsc_dir"
        break
    else
        # Move up one directory
        current_dir=$(dirname "$current_dir")
    fi
done

if [ "$current_dir" == "passwordList" ]; then
    echo "No 'rsc' directory found."
    exit 15
fi