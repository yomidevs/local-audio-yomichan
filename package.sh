#!/bin/bash

# Usage:
# ./package.sh
# OR
# ./package.sh --dev

rm ./localaudio.ankiaddon
cd plugin
#zip -r ../localaudio.ankiaddon *.py source/*.py version.txt user_files/.placeholder manifest.json
zip -r ../localaudio.ankiaddon *.py source/*.py version.txt user_files/.placeholder

if [[ "$1" == "--dev" ]]; then
    # update zip with manifest
    zip -r ../localaudio.ankiaddon manifest.json
fi

cd ..
