#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 input_file hash_type"
    exit 1
fi

source global_config.sh
input_file="$1"
hash_type="$2"

#sqlite3 "$DB_FILE" "CREATE TABLE IF NOT EXISTS $TABLE_NAME (MD5 TEXT PRIMARY KEY, password TEXT);"

while read -r line; do
    hash=$(echo "$line" | cut -d ' ' -f 1)

    existing_hash=$(sqlite3 "$DB_FILE" "SELECT $hash_type FROM $TABLE_NAME WHERE $hash_type='$hash';")

    if [ -z "$existing_hash" ]; then
        sqlite3 "$DB_FILE" "INSERT INTO $TABLE_NAME ($hash_type) VALUES ('$hash');"
        echo "Inserted hash: $hash"
    else
        echo "Hash already exists: $hash. Skipping."
    fi
done < "$input_file"

echo "Data imported into the database."

#tested on ./to_hashpass_table.sh uzivatel/uzivatele_hashes.txt hashpass.db