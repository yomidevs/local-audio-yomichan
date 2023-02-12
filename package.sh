#zip -r localaudio_sql09__2023_01_15.ankiaddon __init__.py ./make_nhk16_db.py manifest.json meta.json user_files
cd plugin
zip -r ../localaudio.ankiaddon *.py source/*.py version.txt user_files/.placeholder
cd ..
