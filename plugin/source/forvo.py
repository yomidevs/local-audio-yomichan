import sqlite3
from pathlib import Path
from typing import Final

from .audio_source import AudioSource, AudioSourceData
from ..consts import *
from ..util import get_program_root_path


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
