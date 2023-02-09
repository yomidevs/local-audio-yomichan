import os
import sqlite3

from .audio_source import AudioSource, AudioSourceData
from ..util import get_db_path, is_kana


class JPodAudioSource(AudioSource):
    def create_table(self):
        table_name = self.data.id
        start = self.data.media_dir

        drop_table_sql = f"DROP TABLE IF EXISTS {table_name}"
        create_table_sql = f"""
           CREATE TABLE {table_name} (
               id integer PRIMARY KEY,
               expression text NOT NULL,
               reading text,
               file text NOT NULL,
               priority integer NOT NULL
           );
        """

        # basic optimization
        #
        # The most important optimization is `expression`, reading and priority are not nearly
        # as important. However, because we aren't actually adding any data to the database,
        # only the query has to be optimized, and we can assume initialization costs
        # are not important.
        #
        # - `reading` is in the index in order to break ties from the first column
        #   See 1.6. Multi-Column Indices
        # - `priority` is in the index to change the `ORDER BY priority` into a no-op.
        #   See 3.1. Searching And Sorting With A Multi-Column Index
        #   https://www.sqlite.org/queryplanner.html
        create_index_sql = f"""
            CREATE INDEX idx_{table_name} ON {table_name}(expression, reading, priority);
        """

        with sqlite3.connect(get_db_path()) as conn:
            cur = conn.cursor()
            cur.execute(drop_table_sql)
            cur.execute(create_table_sql)
            cur.execute(create_index_sql)

            for root, _, files in os.walk(start, topdown=False):
                for name in files:
                    path = os.path.join(root, name)
                    relative_path = os.path.relpath(path, start)

                    if not name.endswith(".mp3"):
                        print(
                            f"({self.__class__.__name__}) skipping non-mp3 file: {relative_path}"
                        )
                        continue

                    parts = name.removesuffix(".mp3").split(" - ")
                    if len(parts) != 2:
                        print(
                            f"({self.__class__.__name__}) skipping file with ' - ' sep: {relative_path}"
                        )
                        continue

                    # usually, jpod file names are formatted as:
                    # "reading - term.mp3"
                    # however, sometimes, the reading section is just the term (even if the term is kanji)
                    reading, expr = parts

                    sql = f"INSERT INTO {table_name} (expression, reading, file, priority) VALUES (?,?,?,?)"

                    if reading == expr:
                        if is_kana(reading):
                            # it's likely safe to store kana only words like this
                            cur.execute(sql, (reading, reading, relative_path, 2))
                        else:
                            sql = f"INSERT INTO {table_name} (expression, reading, file, priority) VALUES (?,NULL,?,?)"
                            cur.execute(sql, (reading, relative_path, 1))
                    else:
                        cur.execute(sql, (expr, reading, relative_path, 2))
            conn.commit()

    def get_name(self, row):
        return "JPod101"


JPOD_DATA = AudioSourceData("jpod", "user_files/jpod_files")
JPOD_AUDIO_SOURCE = JPodAudioSource(JPOD_DATA)
