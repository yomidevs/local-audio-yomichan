rm ./localaudio.ankiaddon
cd plugin
# manifest.json is ignored if downloaded from ankiweb, so it's safe to set the name to whatever
zip -r ../localaudio.ankiaddon *.py source/*.py version.txt user_files/.placeholder manifest.json
cd ..
