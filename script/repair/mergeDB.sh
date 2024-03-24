#!/bin/bash
import sqlite3

if [ "$#" -ne 1 ]; then
   echo "Usage: $0 <DB file>"
   exit 1
fi

# Database file
DB_FILE="$1"
TABLE_NAME="pass_hash"

#if flock -n 9; then
#    echo "Database is not locked."
#    # Release the lock after checking
#    flock -u 9
#else
#    echo "Database is locked., try check databse execute permissions"
#fi

bypassword(){
 SQL_QUERY=$(cat <<EOF
SELECT password
FROM $TABLE_NAME
WHERE password IS NOT NULL AND password != '' AND password IN (
    SELECT password
    FROM $TABLE_NAME
    GROUP BY password
    HAVING COUNT(*) > 1
)
  GROUP BY password
EOF
)

  # Execute the SQL query and echo unique passwords
  sqlite3 "$DB_FILE" "$SQL_QUERY" | while read -r password; do
    ADDITIONAL_INFO_QUERY=$(cat << EOF
        SELECT ID, MD5, SHA1
        FROM $TABLE_NAME
        WHERE password = "$password";
EOF
  )
    echo "Password: $password"
    l_md5=$(md5sum <<< "$password" | awk '{print $1}')
    l_sha1=$(sha1sum <<< "$password" | awk '{print $1}')

    #echo "Counted MD5: $l_md5, SHA1: $l_sha1"
    d="DELETE FROM $TABLE_NAME WHERE password = '$password';"
    #echo "$d"
    sqlite3 "$DB_FILE" "$d"
    i="INSERT INTO $TABLE_NAME (password,MD5,SHA1) VALUES ('$password','$l_md5','$l_sha1');"
    #echo "$i"
    sqlite3 "$DB_FILE" "$i"

    #sqlite3 "$DB_FILE" "$ADDITIONAL_INFO_QUERY" | while IFS='|' read -r ID MD5 SHA1; do
    #  echo "$ID $MD5 $SHA1"
    #if [ "$l_md5" != "$MD5" ] && [ -n "$MD5" ]; then
    #    echo -e "\e[31m Conflict with MD5: counted $l_md5 is not $MD5 ($ID) \e[0m"
    #    sqlite3 "$DB_FILE" "UPDATE $TABLE_NAME SET password = NULL WHERE ID = '$ID';"
    #  elif [ "$l_sha1" != "$SHA1" ] && [ -n "$SHA1" ]; then
    #    echo -e "\e[31m Conflict with SHA1: counted $l_sha1 is not $SHA1 ($ID) \e[0m"
    #    sqlite3 "$DB_FILE" "UPDATE $TABLE_NAME SET password = NULL WHERE ID = '$ID';"
    #  else
    #  echo "Ok,$ID deleted  $MD5 $SHA1"
    #  sqlite3 "$DB_FILE" "DELETE FROM $TABLE_NAME WHERE ID = $ID;"
    #else

    #fi
  #done
done
}
merge() {
    hash_type=$1
    second_type=''

    if [[ "$hash_type" != "MD5" ]] && [[ "$hash_type" != "SHA1" ]]; then
      exit 42
    fi

    if [ "$hash_type" == 'MD5' ]; then
        second_type='SHA1'
    fi
    if [ "$hash_type" == 'SHA1' ]; then
        second_type='MD5'
    fi


    echo "merge $hash_type $second_type"

SQL_MERGE_QUERY=$(cat <<EOF
SELECT $hash_type
FROM $TABLE_NAME
  WHERE $hash_type IS NOT NULL AND $hash_type != '' AND $hash_type IN (
    SELECT $hash_type
      FROM $TABLE_NAME
      GROUP BY $hash_type
      HAVING COUNT(*) > 1
    )
    GROUP BY $hash_type
EOF
)
sqlite3 "$DB_FILE" "$SQL_MERGE_QUERY" | while read -r hash; do
  echo "$hash_type: $hash"
    ADDITIONAL_INFO_QUERY=$(cat << EOF
      SELECT ID, password, $second_type
      FROM $TABLE_NAME
      WHERE $hash_type = '$hash';
EOF
)

  pass=''
  r_SHA1=''


  while IFS='|' read -r ID password second_hash; do
    if [ -n "$pass" ] && [ -n "$password" ] && [ "$pass" != "$password" ]; then
        echo -e "\e[31m Conflict with password: $pass is not $password ($ID) \e[0m"
    elif [ -n "$r_SHA1" ] && [ -n "$second_hash" ] && [ "$r_SHA1" != "$second_hash" ]; then
        echo -e "\e[31m Conflict with SHA1: $r_SHA1 is not $second_hash ($ID) \e[0m"
    else
        echo "Ok, $ID is safe to merge to result $password $second_hash"
        if [ -n "$password" ]; then
            pass="$password"
        fi
        if [ -n "$second_hash" ]; then
            r_SHA1="$second_hash"
        fi
        echo delete "$ID"
        # Uncomment the following line when you're ready to delete the rows
        sqlite3 "$DB_FILE" "DELETE FROM $TABLE_NAME WHERE ID = $ID;"
    fi
    echo "co $pass:$hash:$r_SHA1"
done < <(sqlite3 "$DB_FILE" "$ADDITIONAL_INFO_QUERY")

    echo "tak tady co $pass:$hash:$r_SHA1"
    sqlite3 "$DB_FILE" "INSERT OR IGNORE INTO $TABLE_NAME (password,$hash_type,$second_type) VALUES ('$pass','$hash','$r_SHA1');"
done
}

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <DB_FILE>"
    exit 1
fi

bypassword
#merge "MD5"
#merge "MD5"
#merge "SHA1"
