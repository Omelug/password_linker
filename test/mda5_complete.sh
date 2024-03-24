#!/bin/bash

source global_config.sh
PASSWORD_COLUMN="password"
HASHED_COLUMN="MD5"

# Fetch the passwords from the database where hashed column is NULL
passwords=$(sqlite3 $DB_FILE "SELECT $PASSWORD_COLUMN FROM $TABLE_NAME WHERE $HASHED_COLUMN IS NULL;")

# Loop through each password, hash it, and insert the hashed value into the new column
for password in $passwords; do
    # Check if hashed column is already populated
    existing_hash=$(sqlite3 $DB_FILE "SELECT $HASHED_COLUMN FROM $TABLE_NAME WHERE $PASSWORD_COLUMN='$password';")
    if [ -z "$existing_hash" ]; then
        hashed_password=$(echo -n "$password" | md5sum | awk '{print $1}')
        sqlite3 $DB_FILE "UPDATE $TABLE_NAME SET $HASHED_COLUMN='$hashed_password' WHERE $PASSWORD_COLUMN='$password';"
        #echo "Hashed password for $password."
    else
        echo "Hashed column already populated for $password. Skipping."
    fi
done

echo "Hashing complete!"
