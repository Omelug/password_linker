#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 $1"
    exit 1
fi

hash_cmd=0
HASHED_COLUMN=$1

if [ "$1" = "MD5" ]; then
    hash_cmd="md5sum"
elif [ "$1" = "SHA1" ]; then
    hash_cmd="sha1sum"
else
  exit 42
fi


source global_config.sh
PASSWORD_COLUMN="password"

# Fetch the passwords from the database where hashed column is NULL
passwords=$(sqlite3 $DB_FILE "SELECT $PASSWORD_COLUMN FROM $TABLE_NAME WHERE $HASHED_COLUMN IS NULL;")
while IFS= read -r password; do
    echo "Hashed password for $password."
    # Check if hashed column is already in database
    existing_hash=$(sqlite3 $DB_FILE "SELECT $HASHED_COLUMN FROM $TABLE_NAME WHERE $PASSWORD_COLUMN='$password';")
    if [ -z "$existing_hash" ]; then
        hashed_password=$(echo -n "$password" | $hash_cmd | awk '{print $1}')
        #sqlite3 $DB_FILE "UPDATE $TABLE_NAME SET $HASHED_COLUMN='$hashed_password' WHERE $PASSWORD_COLUMN='$password';"
    #else
        #echo "Hashed column already populated for $password. Skipping."
    fi
    echo "Hashed password for $password:$existing_hash."
done < "$passwords"

echo "Hashing complete!"
