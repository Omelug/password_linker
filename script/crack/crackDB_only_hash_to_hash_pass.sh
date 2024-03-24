#!/bin/bash


TABLE_NAME="pass_hash"

force_override=false
hash_type="MD5"
temp_output_file="temp_output.txt"
display_help() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -h, --help    Display this help message"
    echo "  -i, --input   Specify the input file containing hashes (default: hashes.txt)"
    echo "  -o, --output  Specify the output file for results (default: output.txt)"
    echo "  -d, --database Specify the SQLite database file (default: your_database.db)"
    echo "  -t, --table    Specify the database table containing MD5 and pass columns (default: your_table)"
    echo "  -f, --force   Force override the output file if it exists"
    echo "  -H, --hash-type     Specify the hash type (e.g., SHA or MD5)"
    exit 0
}

while getopts ":h:i:o:d:t:fH:-help" opt; do
  case $opt in
    h|--help) display_help ;;
    i|--input) input_file="$OPTARG" ;;
    o|--output) output_file="$OPTARG" ;;
    d|--database) sqlite_db="$OPTARG" ;;
    t|--table) database_table="$OPTARG" ;;
    f|--force) force_override=true ;;
    H|--hash-type) hash_type="$OPTARG" ;;
    \?) echo "Invalid option: -$OPTARG" >&2; exit 1 ;;
    :) echo "Option -$OPTARG requires an argument." >&2; exit 1 ;;
  esac
done

if [ -e "$output_file" ] && [ "$force_override" != true ]; then
    echo "Error: Output file '$output_file' already exists. Use -f to force override."
    exit 1
fi

while IFS= read -r hash_line; do
    hash=$(echo "$hash_line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')

     hash=$(echo "$hash_line" | awk -F':' '{print $1}')

    result=$(sqlite3 "$sqlite_db" "SELECT password FROM $TABLE_NAME WHERE $hash_type='$hash';")

    echo "$hash:$result"

    if [ -n "$result" ]; then
        echo "$hash:$result" >> "$temp_output_file"
    else
        echo "$hash:" >> "$temp_output_file"
    fi
done < "$input_file"

mv "$temp_output_file" "$output_file"
