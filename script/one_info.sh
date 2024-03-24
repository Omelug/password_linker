#!/bin/bash

source global_config.sh

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <PASSWORD_COLUMN> <PASSWORD_FILE>"
    exit 1
fi

PASSWORD_COLUMN="$1"
PASSWORD_FILE="$2"

# Loop through each password in the file and insert it into the table
while IFS= read -r password; do
    # Escape single quotes in the password for SQL
    escaped_password=$(echo "$password" | sed "s/'/''/g")

    sqlite3 $DB_FILE "INSERT INTO $TABLE_NAME ($PASSWORD_COLUMN) VALUES ('$escaped_password');"

    echo "Inserted password: $password"
done < "$PASSWORD_FILE"

echo "Insertion complete!"
