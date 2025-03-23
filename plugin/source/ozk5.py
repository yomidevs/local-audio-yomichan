from __future__ import annotations  # for Python 3.7-3.9

import json
import sqlite3
from typing import Optional, Final, TypedDict

from .audio_source import AudioSource
from ..jp_util import split_into_mora, hiragana_to_katakana


"""
This is based on the schema for OZK5 with entries, kanji_index, and kana_index:
{
  "meta": {
    "name": "旺文社全訳古語辞典",
    "year": 2025,
    "version": 1,
    "media_dir": "media"
  },
  "entries": [
    {
      "kanji": "亜",
      "kana": "あ",
      "audio_file": "audio.aac"
    },
    ...
  ],
  "kanji_index": {
    "亜": [0],
    ...
  },
  "kana_index": {
    "あ": [0],
    ...
  }
}
"""


class OZK5Data(TypedDict):
    kanji: str
    kana: str
    audio_file: str
    pitch_number: str


class OZK5Meta(TypedDict):
    name: str
    year: int
    version: int
    media_dir: str


class OZK5Index(TypedDict):
    meta: OZK5Meta
    entries: list[OZK5Data]
    kanji_index: dict[str, list[int]]
    kana_index: dict[str, list[int]]


SQL: Final[
    str
] = "INSERT INTO entries (expression, reading, source, display, file) VALUES (?,?,?,?,?)"


class OZK5AudioSource(AudioSource):
    def get_display_text(self, entry: OZK5Data) -> Optional[str]:
        """
        displays as katakana with number and downstep, i.e. "ヨ＼ム [1]"
        """
        reading = entry.get("kana", None)
        if reading is None:
            return None
        mora_list = split_into_mora(hiragana_to_katakana(reading))
        try:
            if entry["pitch_number"] == "?":
                return None
            pitch_accent = int(entry["pitch_number"])
        except Exception:
            # handle non-integer pitch numbers
            print(f"({self.data.id}) pitch_number is not an integer: {entry}")
            return None
        if pitch_accent > 0:
            mora_list.insert(pitch_accent, "＼")
        return "".join(mora_list) + f" [{pitch_accent}]"

    def add_entries(self, connection: sqlite3.Connection):
        cur = connection.cursor()
        index_file = self.get_media_dir_path().joinpath("index.json")

        if not index_file.is_file():  # don't error if it simply doesn't exist
            print(f"({self.__class__.__name__}) Cannot find entries file: {index_file}")
            return

        with open(index_file, encoding="utf-8") as f:
            data: OZK5Index = json.load(f)
            entries = data["entries"]
            media_dir = data["meta"].get("media_dir", "media")

            # Process all entries
            for entry in entries:
                expression = entry["kanji"] or entry["kana"]  # Use kana if no kanji
                reading = entry["kana"]
                audio_file = entry["audio_file"]
                
                fullpath = self.get_media_dir_path().joinpath(media_dir).joinpath(audio_file)
                relpath = fullpath.relative_to(self.get_media_dir_path())
                
                if not fullpath.is_file():
                    continue
                
                display = self.get_display_text(entry)
                cur.execute(SQL, (expression, reading, self.data.id, display, str(relpath)))
                
                # If we have kanji, add another entry with kana as expression
                # so it can be found by both kanji and kana lookups
                if entry["kanji"] and entry["kanji"] != entry["kana"]:
                    cur.execute(SQL, (reading, reading, self.data.id, display, str(relpath)))

        cur.close()
        connection.commit()