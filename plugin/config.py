"""
Source schema:

- type: "jpod" | "nhk" | "forvo" | "ajt_jp"
    - ajt_jp is short for AJT Japanese
    - If you ever create a new source, I recommend following the AJT Japanese schema, as it's well defined compared to the others
- id: string id used as the id in the "source" column, as well as the parameter in the url
- path: string, path to the source files
- display: string used to display in Yomitan. Uses %s for the "DISPLAY" column.
"""

import json
from pathlib import Path
from typing import TypedDict, Final, Type

from .source.jpod import JPodAudioSource
from .source.nhk16 import NHK16AudioSource
from .source.forvo import ForvoAudioSource
from .source.ajt_jp import AJTJapaneseSource

from .consts import CONFIG_FILE_NAME, DEFAULT_CONFIG_FILE_NAME
from .util import get_config_dir, get_data_dir, get_program_root_dir
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


def get_default_config_file():
    return get_program_root_dir().joinpath(DEFAULT_CONFIG_FILE_NAME)


def get_config_file():
    return get_config_dir().joinpath(CONFIG_FILE_NAME)


def read_config() -> JsonConfig:
    """
    read default config, unless user config is found
    """
    default_config_file = get_default_config_file()
    with open(default_config_file, encoding="utf-8") as f:
        config = json.load(f)

    config_file = get_config_file()

    if config_file.is_file():
        with open(config_file, encoding="utf-8") as f:
            user_config = json.load(f)
            for k, v in user_config.items():
                config[k] = v

    return config


def get_all_sources() -> dict[str, AudioSource]:
    """
    note: insertion order is important for this to work
    """
    sources = {}
    config = read_config()
    for source_json in config["sources"]:
        id = source_json["id"]
        type = source_json["type"]
        path = source_json["path"]
        display = source_json["display"]

        # checks for source_meta.json
        source_meta_path = get_data_dir() / path / "source_meta.json"
        if source_meta_path.is_file():
            with open(source_meta_path, encoding="utf-8") as f:
                source_meta = json.load(f)
                meta_type = source_meta.get("type", None)
                if meta_type is not None:
                    type = meta_type

        AudioSourceClass = SOURCE_TYPES[type]
        data = AudioSourceData(id, path, display)
        source = AudioSourceClass(data)
        sources[id] = source
    return sources


ALL_SOURCES = get_all_sources()
