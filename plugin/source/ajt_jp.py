from __future__ import annotations  # for Python 3.7-3.9

import json
import sqlite3
from typing import Optional, Final, TypedDict
# THIS REQUIRES A PIP INSTALL, making it impossible to use in Anki...
#from typing_extensions import NotRequired

from .audio_source import AudioSource
from ..jp_util import split_into_mora, hiragana_to_katakana


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
    #kana_reading: NotRequired[str]
    kana_reading: str
    pitch_number: str
    #pitch_pattern: NotRequired[str]
    pitch_pattern: str


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
        """
        displays as katakana with number and downstep, i.e. "ヨ＼ム [1]"
        """
        reading = ajt_file.get("kana_reading", None)
        if reading is None:
            return None
        mora_list = split_into_mora(hiragana_to_katakana(reading))
        try:
            if ajt_file["pitch_number"] == "?":
                return None
            pitch_accent = int(ajt_file["pitch_number"])
        except Exception:
            # apparently, pitch_number can be something like "0+2", in which case we look for pitch_pattern
            pitch_pattern = ajt_file.get("pitch_pattern", None)
            if pitch_pattern is not None:
                return pitch_pattern
            print(f"({self.data.id}) pitch_number is not an integer: {ajt_file}")
            return None
        if pitch_accent > 0:
            mora_list.insert(pitch_accent, "＼")
        return "".join(mora_list) + f" [{pitch_accent}]"

    def add_entries(self, connection: sqlite3.Connection):
        cur = connection.cursor()
        index_file = self.get_media_dir_path().joinpath("index.json")

        if not index_file.is_file(): # don't error if it simply doesn't exist
            print(f"({self.__class__.__name__}) Cannot find entries file: {index_file}")
            return

        with open(index_file, encoding="utf-8") as f:
            entries: AJTIndex = json.load(f)
            files = entries["files"]

            for expression, word_files in entries["headwords"].items():
                for word_file in word_files:
                    fullpath = self.get_media_dir_path().joinpath("media").joinpath(word_file)
                    relpath = fullpath.relative_to(self.get_media_dir_path())
                    if not fullpath.is_file():
                        continue
                    ajt_file = files.get(word_file, None)
                    if ajt_file is not None:
                        reading = ajt_file.get("kana_reading", None)
                        display = self.get_display_text(ajt_file)
                        cur.execute(SQL, (expression, reading, self.data.id, display, str(relpath)))

        cur.close()
        connection.commit()
