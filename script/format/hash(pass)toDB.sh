#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 input_file hash_type database_file"
    exit 1
fi

input_file="$1"
hash_type="$2"
database_file="$3"

sqlite3 "$database_file" "CREATE TABLE IF NOT EXISTS pass_hash ($hash_type TEXT PRIMARY KEY, password TEXT);"

while read -r line; do
    hash=$(echo "$line" | cut -d ' ' -f 1)
    password=$(echo "$line" | sed -n 's/.*(\(.*\))/\1/p')

    if [ -z "$(sqlite3 "$database_file" "SELECT 1 FROM pass_hash WHERE $hash_type = '$hash';")" ]; then
        sqlite3 "$database_file" "INSERT INTO pass_hash ($hash_type, password) VALUES ('$hash', '$password');"
        echo "Inserted: $hash:$password"
    else
        echo "Skipped - Hash already exists: $hash:$password"
    fi

    #echo "$hash:$password"
done < "$input_file"

echo "Data imported into the database."
