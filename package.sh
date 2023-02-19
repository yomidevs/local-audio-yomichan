rm ./localaudio.ankiaddon
cd plugin
mkdir user_files
touch user_files/.placeholder
zip -r ../localaudio.ankiaddon *.py source/*.py version.txt user_files/.placeholder
cd ..
