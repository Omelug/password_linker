#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 input_file "
    exit 1
fi
source global_config.sh
input_file="$1"

skip_cnt=0
insert_cnt=0

#echo "$DB_FILE $TABLE_NAME"

while IFS= read -r line; do
    password=$(echo "$line" | cut -d ' ' -f 1)

    md5=$(echo -n "$password" | md5sum | awk '{print $1}')
    sha1=$(echo -n "$password" | sha1sum | awk '{print $1}')

    existing_password=$(sqlite3 "$DB_FILE" "SELECT password FROM $TABLE_NAME WHERE password = '$password';")

    if [ -z "$existing_password" ]; then
        sqlite3 "$DB_FILE" "INSERT OR IGNORE INTO $TABLE_NAME (password, MD5, SHA1) VALUES ('$password', '$md5', '$sha1');"
        #sqlite3 "$DB_FILE" "INSERT OR IGNORE INTO $TABLE_NAME (password) VALUES ('$password');"
        ((insert_cnt++))
    else
        ((skip_cnt++))
        #echo "Password already exists. Skipping insertion."
    fi
    echo "skiped:$skip_cnt, inserted:$insert_cnt"
done < "$input_file"

echo "skiped:$skip_cnt, inserted:$insert_cnt STOP"