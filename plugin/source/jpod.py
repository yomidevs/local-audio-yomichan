import sqlite3
from pathlib import Path
from typing import Final

from .audio_source import AudioSource, AudioSourceData
from ..util import get_program_root_path
from ..jp_util import is_kana


class JPodAudioSource(AudioSource):
    def add_entries(self, connection: sqlite3.Connection):
        cur = connection.cursor()
        sql = f"""
        INSERT INTO entries
          (expression, reading, source, file)
        VALUES
          (?,?,?,?)
            """

        for path in self.find_media_files():
            relative_path = str(path.relative_to(self.get_media_dir_path()))
            basename_noext = path.stem
            parts = basename_noext.split(" - ")

            # Cannot parse required fields from a filename missing a " - " separator.
            if len(parts) != 2:
                print(
                    f"({self.__class__.__name__}) skipping file without ' - ' sep: {relative_path}"
                )
                continue

            # usually, jpod file names are formatted as:
            # "reading - term.ext"
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


#JPOD_DATA: Final = AudioSourceData("jpod", "user_files/jpod_files")
#JPOD_AUDIO_SOURCE: Final = JPodAudioSource(JPOD_DATA)
