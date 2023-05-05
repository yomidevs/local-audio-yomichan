import os
import json
import sqlite3
from typing import Final, TypedDict, Optional

from .audio_source import AudioSource
from ..util import split_into_mora, get_program_root_path


"""
This is based off of the schema found under `AudioSource`
(https://github.com/Ajatt-Tools/Japanese/blob/f5bbbad901a9ffc4dbf00f244de19f3a9a8120bd/helpers/audio_manager.py#L156):

{
  "meta": {
    // ... (not important for this add-on)
  },
  "headwords": {
    // maps words to file
  },
  "files": {
    // maps file to {"kana_reading": ..., "pitch_number": ...}
    // WARNING: "kana_reading" may be katakana!
    // WARNING: "pitch_number" maps to a string for whatever reason
  },
}
"""


class AJTFile(TypedDict):
    kana_reading: str
    pitch_number: str


class AJTMeta(TypedDict):
    version: int
    # other fields are currently ignored for the purposes of this add-on


class AJTIndex(TypedDict):
    meta: AJTMeta
    headwords: dict[str, list[str]]
    files: dict[str, AJTFile]


SQL: Final[
    str
] = "INSERT INTO entries (expression, reading, source, display, file) VALUES (?,?,?,?,?)"


class AJTJapaneseSource(AudioSource):
    def get_display_text(self, ajt_file: AJTFile) -> Optional[str]:
        mora_list = split_into_mora(ajt_file["kana_reading"])
        try:
            pitch_accent = int(ajt_file["pitch_number"])
        except Exception:
            print(f"pitch_number is not an integer: {ajt_file}")
            return None
        mora_list.insert(pitch_accent, "＼")
        return "".join(mora_list) + f" [{pitch_accent}]"

    def add_entries(self, connection: sqlite3.Connection):
        cur = connection.cursor()

        program_root_path = get_program_root_path()
        index_file = os.path.join(program_root_path, self.data.media_dir, "index.json")

        with open(index_file, encoding="utf-8") as f:
            entries: AJTIndex = json.load(f)
            files = entries["files"]

            for expression, word_files in entries["headwords"].items():
                for word_file in word_files:
                    file = os.path.join("media", word_file)  # relative path
                    ajt_file = files.get(word_file, None)
                    if ajt_file is not None:
                        reading = ajt_file["kana_reading"]
                        display = self.get_display_text(ajt_file)
                        cur.execute(SQL, (expression, reading, self.data.id, display, file))

        cur.close()
        connection.commit()
