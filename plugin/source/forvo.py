import os
import sqlite3

from .audio_source import AudioSource, AudioSourceData
from ..consts import *


class ForvoAudioSource(AudioSource):
    def add_entries(self, connection: sqlite3.Connection):
        start = self.data.media_dir

        sql = "INSERT INTO entries (expression, source, speaker, file) VALUES (?,?,?,?)"
        cur = connection.cursor()

        for root, _, files in os.walk(start, topdown=False):
            for name in files:
                path = os.path.join(root, name)
                relative_path = os.path.relpath(path, start)

                if not name.endswith(".mp3"):
                    print(f"(ForvoAudioSource) skipping non-mp3 file: {relative_path}")
                    continue

                speaker = os.path.basename(root)
                expr = os.path.splitext(name)[0]

                cur.execute(sql, (expr, self.data.id, speaker, relative_path))

        cur.close()
        connection.commit()

    def get_name(self, row):
        return f"Forvo ({row[SPEAKER]})"


FORVO_DATA = AudioSourceData("forvo", "user_files/forvo_files")
FORVO_AUDIO_SOURCE = ForvoAudioSource(FORVO_DATA)
