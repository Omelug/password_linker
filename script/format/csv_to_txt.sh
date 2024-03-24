#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 input_csv column_number output_txt"
    exit 1
fi

input_csv="$1"
column_number="$2"
output_txt="$3"

empty_value="<blank>"

# Extract the specified column from the CSV file and save it to the text file
awk -F ',' -v col="$column_number" '$col != '$empty_value' {print $col}' "$input_csv" > "$output_txt"

echo "Column $column_number of the CSV file has been converted to '$output_txt'."

#tested on ./csv_to_txt.sh uzivatel/original/uzivatele.txt 5 uzivatel/uzivatele_hashes.txt