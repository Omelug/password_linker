#!/bin/bash

input_folder=$1

if [ -z "$input_folder" ]; then
  echo "Usage: $0 <input_folder>"
  exit 1
fi


input_folder="test/test_rsc_folder"
echo "Input folder: $input_folder"

rsc_folder="rsc"
resource_folder="$rsc_folder/$(basename "$input_folder")"
original_folder="$resource_folder/original"

echo "Input folder: $rsc_folder"

if [ -d "$rsc_folder" ]; then
  if [ -d "$resource_folder" ]; then
    echo "Warning: $resource_folder folder already exists."
  else
    if [ -d "$original_folder" ]; then
      echo "Warning: $original_folder folder already exists."
    else
      mkdir -p "$original_folder"
      echo "Created $original_folder folder."
    fi
  fi

  cp -R "$input_folder/." "$original_folder/"

else
    echo "Directory $rsc_folder does not exist."
fi