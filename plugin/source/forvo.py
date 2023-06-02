import sqlite3

from .audio_source import AudioSource
from ..consts import *


class ForvoAudioSource(AudioSource):
    def add_entries(self, connection: sqlite3.Connection):
        sql = "INSERT INTO entries (expression, source, speaker, display, file) VALUES (?,?,?,?,?)"
        cur = connection.cursor()

        for path in self.find_media_files():
            relative_path = str(path.relative_to(self.get_media_dir_path()))
            speaker = path.parent.name
            display = speaker
            expr = path.stem
            cur.execute(sql, (expr, self.data.id, speaker, display, relative_path))

        cur.close()
        connection.commit()
