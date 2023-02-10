import os
from pathlib import Path
import sqlite3

from .util import get_db_path, get_program_root_path
from .all_sources import SOURCES

def android_gen():
    i = 0
    original_db_path = get_db_path()
    android_db_path = os.path.join(
        get_program_root_path(),
        "android.db"
    )
    with sqlite3.connect(original_db_path) as connection:
        og_cursor = connection.cursor()
        with sqlite3.connect(android_db_path) as android_connection:
            android_cursor = android_connection.cursor()

            android_write(og_cursor, android_cursor)

            android_cursor.close()
        og_cursor.close()

# original cursor, android cursor
def android_write(og_cur, a_cur):

    drop_table_sql = f"DROP TABLE IF EXISTS android"
    create_table_sql = f"""
       CREATE TABLE android (
           file text NOT NULL,
           source text NOT NULL,
           data blob NOT NULL
       );
    """
    create_index_sql = f"""
        CREATE INDEX idx_android ON android(file, source);
    """
    a_cur.execute(drop_table_sql)
    a_cur.execute(create_table_sql)
    a_cur.execute(create_index_sql)

    sql = f"""
        INSERT INTO android (file, source, data) VALUES (?,?,?)
        """

    for source in SOURCES:
        i = 0
        all_files_query = f"""
            SELECT file FROM {source.data.id}
            """

        rows = og_cur.execute(all_files_query).fetchall()
        for row in rows:
            i += 1
            file_name = row[0]
            full_file_path = os.path.join(
                get_program_root_path(),
                source.get_media_dir_path(),
                file_name
            )
            if not Path(full_file_path).is_file():
                print(f"(android_gen) Cannot find file: {full_file_path}")
                continue

            print(full_file_path)
            with open(full_file_path, 'rb') as file:
                a_cur.execute(sql, (file_name, source.data.id, file.read()))

            if i > 20:
                break


if __name__ == "__main__":
    android_gen()


def init_db(force_init: bool = False):
    print("Initializing database. This make take a while...")
    for source in SOURCES:
        source.init_table(force_init)
    print("Finished initializing database!")


