#!/bin/bash

input_file="rsc/hashpass_test.db"
DB_FILE="../../rsc/breach_BC_1_CZ/original/only_pass.txt"
TABLE_NAME="pass_hash"

skip_cnt=0
insert_cnt=0

# Function to hash the password
hash_password() {
    local password="$1"
    local md5=$(echo -n "$password" | md5sum | awk '{print $1}')
    local sha1=$(echo -n "$password" | sha1sum | awk '{print $1}')
    echo "$md5" "$sha1"
}

# Export function for use by parallel
export -f hash_password

# Process lines in parallel and store the results in a temporary file
cat "$input_file" | parallel -j 4 --line-buffer \
    'password=$(echo {} | cut -d " " -f 1); hash_result=$(hash_password "$password"); echo "$password $hash_result" >> temp_results.txt'

# Process the results file sequentially and insert into the database
while IFS= read -r line; do
    password=$(echo "$line" | cut -d ' ' -f 1)
    hash_result=$(echo "$line" | cut -d ' ' -f 2-)
    read -r md5 sha1 <<< "$hash_result"

    existing_password=$(sqlite3 "$DB_FILE" "SELECT password FROM $TABLE_NAME WHERE password = '$password';")

    if [ -z "$existing_password" ]; then
        sqlite3 "$DB_FILE" "INSERT OR IGNORE INTO $TABLE_NAME (password, MD5, SHA1) VALUES ('$password', '$md5', '$sha1');"
        ((insert_cnt++))
    else
        ((skip_cnt++))
    fi
    echo "skipped: $skip_cnt, inserted: $insert_cnt"
done < temp_results.txt

# Clean up temporary file
rm temp_results.txt

echo "skipped: $skip_cnt, inserted: $insert_cnt STOP"