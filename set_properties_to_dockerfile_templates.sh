#!/bin/bash

set -a # turn on auto-export
. properties/configuration.properties
set -a # turn off auto-export

while IFS= read -r -d '' filename; do
echo "-------------- $filename --------------"
eval "cat <<EOF
$(<$filename)
EOF
" > "${filename%.*}"
done < <(find ./* -name 'Dockerfile.tpl' -print0)
