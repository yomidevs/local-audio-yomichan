"""
Source schema:

- type: "jpod" | "nhk" | "forvo" | "ajt_jp"
    - ajt_jp is short for AJT Japanese
    - If you ever create a new source, I recommend following the AJT Japanese schema, as it's well defined compared to the others
- id: string id used as the id in the "source" column, as well as the parameter in the url
- path: string, path to the source files
- display: string used to display in Yomichan. Uses %s for the "DISPLAY" column.
"""

import os
import json
from typing import TypedDict, Final, Type

from .source.jpod import JPodAudioSource
from .source.nhk16 import NHK16AudioSource
from .source.forvo import ForvoAudioSource
from .source.ajt_jp import AJTJapaneseSource

from .consts import CONFIG_FILE_NAME, DEFAULT_CONFIG_FILE_NAME
from .util import get_program_root_path
from .source.audio_source import AudioSource, AudioSourceData


SOURCE_TYPES: Final[dict[str, Type[AudioSource]]] = {
    "jpod": JPodAudioSource,
    "nhk": NHK16AudioSource,
    "forvo": ForvoAudioSource,
    "ajt_jp": AJTJapaneseSource,
}


class JsonConfigSource(TypedDict):
    type: str
    id: str
    path: str
    display: str


class JsonConfig(TypedDict):
    sources: list[JsonConfigSource]


def get_default_config_path():
    return os.path.join(get_program_root_path(), DEFAULT_CONFIG_FILE_NAME)


def get_config_path():
    return os.path.join(get_program_root_path(), CONFIG_FILE_NAME)


def read_config() -> JsonConfig:
    """
    read default config, unless user config is found
    """
    config_path = get_config_path()
    if not os.path.isfile(config_path):
        default_config_path = get_default_config_path()
        with open(default_config_path, encoding="utf-8") as f:
            return json.load(f)

    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def get_all_sources() -> dict[str, AudioSource]:
    sources = {}
    config = read_config()
    for source_json in config["sources"]:
        id = source_json["id"]
        type = source_json["type"]
        path = source_json["path"]
        display = source_json["display"]
        AudioSourceClass = SOURCE_TYPES[type]
        data = AudioSourceData(id, path, display)
        source = AudioSourceClass(data)
        sources[id] = source
    return sources


ALL_SOURCES = get_all_sources()

