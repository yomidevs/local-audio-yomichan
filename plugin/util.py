import importlib.util
import os
import platform
import ctypes
from functools import lru_cache
from pathlib import Path
from typing import NamedTuple, Optional
from dataclasses import dataclass

from .consts import APP_NAME, DB_FILE_NAME, ANDROID_DB_FILE_NAME, LATEST_VERSION_FILE_NAME



def get_program_root_path():
    """
    gets 'plugin' folder in repo, or the add-on ID on AnkiWeb
    """
    return (
        Path(__file__).parent
    )


def get_anki_data_path():
    return get_program_root_path() / "user_files"


get_anki_config_path = get_anki_data_path


def _get_win_data_path():
    csidl_const = 28  # CSIDL_LOCAL_APPDATA

    buf = ctypes.create_unicode_buffer(1024)
    windll = getattr(ctypes, "windll")
    windll.shell32.SHGetFolderPathW(None, csidl_const, None, 0, buf)

    if any(ord(c) > 255 for c in buf):
        buf2 = ctypes.create_unicode_buffer(1024)
        if windll.kernel32.GetShortPathNameW(buf.value, buf2, 1024):
            buf = buf2

    return Path(buf.value) / APP_NAME


get_win_data_path = lru_cache(maxsize=None)(_get_win_data_path)


get_win_config_path = get_win_data_path


def get_linux_data_path():
    xdg = os.environ.get("XDG_DATA_HOME", "")
    if not xdg.strip():
        return Path.home() / ".local" / "share" / APP_NAME
    else:
        return Path(xdg) / APP_NAME


def get_linux_config_path():
    xdg = os.environ.get("XDG_CONFIG_HOME", "")
    if not xdg.strip():
        return Path.home() / ".config" / APP_NAME
    else:
        return Path(xdg) / APP_NAME


def get_mac_data_path():
    return Path.home() / "Library" / "Application Support" / APP_NAME


get_mac_config_path = get_mac_data_path


def get_data_path():
    """
    returns the native, platform-specific directory for the application data directory
    """
    if importlib.util.find_spec("aqt"):
        return get_anki_data_path()
    elif platform.system() == "Windows":
        return get_win_data_path()
    elif platform.system() == "Linux":
        return get_linux_data_path()
    elif platform.system() == "Darwin":
        return get_mac_data_path()
    else:
        return get_anki_data_path()


def get_config_path():
    """
    returns the native, platform-specific directory for the application config directory
    """
    if importlib.util.find_spec("aqt"):
        return get_anki_config_path()
    elif platform.system() == "Windows":
        return get_win_config_path()
    elif platform.system() == "Linux":
        return get_linux_config_path()
    elif platform.system() == "Darwin":
        return get_mac_config_path()
    else:
        return get_anki_config_path()


def get_db_path():
    return get_data_path().joinpath(DB_FILE_NAME)


def get_android_db_path():
    return get_data_path().joinpath(ANDROID_DB_FILE_NAME)


def get_version_file_path():
    return get_program_root_path().joinpath(LATEST_VERSION_FILE_NAME)


class URLComponents(NamedTuple):
    scheme: str
    netloc: str
    path: str
    params: str
    query: str
    fragment: str


@dataclass(frozen=True)
class QueryComponents:
    expression: str
    reading: Optional[str]
    sources: list[str]
    user: list[str]


AudioSourceJsonEntry = dict[str, str]
AudioSourceJsonList = list[AudioSourceJsonEntry]

