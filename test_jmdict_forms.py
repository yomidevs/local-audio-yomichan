"""
A simple script to only run the function to back-fill the db with jmdict forms, for internal testing purposes.
"""

import sqlite3

from plugin.util import (
    get_db_path,
)
from plugin.db_utils import fill_jmdict_forms

def main():
    with sqlite3.connect(get_db_path()) as conn:
        fill_jmdict_forms(conn)

if __name__ == "__main__":
    main()
