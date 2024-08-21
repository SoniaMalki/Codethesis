#!/bin/bash

dir="$GLOBALSCRATCH/generation"
db_file="$dir/experience.db"
db_save="$dir/experience_old.db"
mv $db_file $db_save

cat <( sqlite3 "$db_save" .dump | grep "^ROLLBACK" -v ) <( echo "COMMIT;" ) | sqlite3 "$db_file"