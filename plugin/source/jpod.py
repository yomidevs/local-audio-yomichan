import os
import sqlite3

from .audio_source import AudioSource, AudioSourceData
from ..util import is_kana


class JPodAudioSource(AudioSource):
    def add_entries(self, connection: sqlite3.Connection):
        start = self.data.media_dir
        cur = connection.cursor()

        sql = f"""
        INSERT INTO entries
          (expression, reading, source, file)
        VALUES
          (?,?,?,?)
            """

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

                if reading == expr:
                    if is_kana(reading):
                        # it's likely safe to store kana only words like this
                        cur.execute(
                            sql, (reading, reading, self.data.id, relative_path)
                        )
                    else:
                        cur.execute(sql, (reading, None, self.data.id, relative_path))
                else:
                    cur.execute(sql, (expr, reading, self.data.id, relative_path))

        cur.close()
        connection.commit()

    def get_name(self, row):
        return "JPod101"


JPOD_DATA = AudioSourceData("jpod", "user_files/jpod_files")
JPOD_AUDIO_SOURCE = JPodAudioSource(JPOD_DATA)
