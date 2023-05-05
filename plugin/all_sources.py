from typing import Final

from .source.audio_source import AudioSource
from .source.jpod import JPOD_AUDIO_SOURCE
from .source.jpod_alt import JPOD_ALT_AUDIO_SOURCE
from .source.nhk16 import NHK16_AUDIO_SOURCE
from .source.forvo import FORVO_AUDIO_SOURCE
from .source.shinmeikai8 import SHINMEIKAI8_AUDIO_SOURCE

SOURCES: Final[list[AudioSource]] = [
    JPOD_AUDIO_SOURCE,
    JPOD_ALT_AUDIO_SOURCE,
    NHK16_AUDIO_SOURCE,
    FORVO_AUDIO_SOURCE,
    SHINMEIKAI8_AUDIO_SOURCE,
]
ID_TO_SOURCE_MAP: Final[dict[str, AudioSource]] = {
    source.data.id: source for source in SOURCES
}
