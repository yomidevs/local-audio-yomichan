from typing import Final

from .audio_source import AudioSourceData
from .ajt_jp_source import AJTJapaneseSource
from ..consts import DISPLAY


class Shinmeikai8AudioSource(AJTJapaneseSource):
    def get_name(self, row):
        return "shinmeikai8 " + row[DISPLAY]


SHINMEIKAI8_DATA: Final = AudioSourceData("shinmeikai8", "user_files/shinmeikai8_files")
SHINMEIKAI8_AUDIO_SOURCE: Final = Shinmeikai8AudioSource(SHINMEIKAI8_DATA)
