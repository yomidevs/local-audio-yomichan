## v1.6.1
- Fixed a bug where some files weren't being opened with utf-8 encoding

## v1.6.0
- Added powershell linking script, so people can install from source on Windows
- Switched some path handling to pathlib (thanks to tsweet64)
- Support a lot more audio formats, like opus, ogg, etc. (thanks to tsweet64)
- Config file now falls back to the default if keys are missing
- Support jmdict_forms.json parsing (to fill in jmdict variant forms)
- Support source_meta.json within each source to override the type
- Change default order to nhk16,shinmeikai8,forvo,jpod

## v1.5.0
- Added a json config file, so sources are slightly easier to configure if necessary

## v1.4.0
- Added shinmeikai 8 audio source (and basic ability to import any AJT Japanese audio source). Thanks to [tatsumoto-ren](https://github.com/Ajatt-Tools/shinmeikai_8_pronunciations_index) for scraping the audio.

## v1.3.3
- Show the time for regenerating the database and for generating the Android database

## v1.3.2
- Added condition in `__init__.py` to only run if it was imported by Anki
- Added `run_server.py` to run the server without opening Anki

## v1.3.1
- Fixed headers: now properly returns `audio/mpeg` and `audio/aac` instead of `text/...`

## v1.3.0
- Changed the database schema for the entries table (ensure that the primary key is not null)
- Generating the database on Anki load now shows a GUI popup
- android.db is now combined with entries.db (two separate tables: `entries` and `android`)
- Added feature to re-generate the database for specific versions

## v1.2.0
- Added `Get number of entries per source` menu option
- Got rid of manifest.json in the resulting localaudio.addon file because it wasn't necessary

## v1.1.3
- Added `user_files` in .addon file so the database can be opened and checked properly

## v1.1.2
- Renamed submenu from `Local Audio` -> `Local Audio Server`

## v1.1.1
- Moved database (entries.db) into `user_files`, so it doesn't get overwritten on each update

## v1.1.0
- Moved options into a submenu (thanks to fsrs4anki helper for the example code)

## v1.0.0
**Major code rewrite:**
- Reworked database format so all sources are now in one giant table, and so one query can get all audio sources correctly
- Separated code into different files, including one for each source

**Other:**
- Removed nhk98 support (due to not having any audio files for it to test it on)
- Fixed JPod + JPod Alt audio sometimes not being fetched because the query does not account for empty expressions or readings
    - Kana only words are stored with both expression and reading being filled (as the same thing)
    - Expression only words are stored without reading i.e. (null)
- Uploaded to ankiweb


## sql_09
- Merged versions `09` and `sql` together

## 09
- Added support for Forvo audio

## sql
- Added support for SQL

## 07

