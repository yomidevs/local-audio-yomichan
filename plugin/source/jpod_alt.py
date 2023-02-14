from typing import Final

from .audio_source import AudioSourceData
from .jpod import JPodAudioSource


class JPodAltAudioSource(JPodAudioSource):
    def get_name(self, row):
        return "JPod101 Alt"


JPOD_ALT_DATA: Final = AudioSourceData("jpod_alternate", "user_files/jpod_alternate_files")
JPOD_ALT_AUDIO_SOURCE: Final = JPodAltAudioSource(JPOD_ALT_DATA)
