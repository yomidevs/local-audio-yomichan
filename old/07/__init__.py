import http.server
import json
import os
import socketserver
import threading

from ast import literal_eval
from collections import defaultdict
from http import HTTPStatus
from pathlib import Path
from urllib.parse import parse_qs
from urllib.parse import quote
from urllib.parse import unquote
from urllib.parse import urlparse

from .make_nhk16_map import make_nhk16_map

HOSTNAME = "localhost"
PORT = 5050

"""
CONSTANTS

*_SOURCE_PARAM
used for the Custom URL (JSON) setting in Yomichan
e.g. ?sources=jpod,nhk16

*_PATH
used for routing audio GET requests from Yomichan

*_MEDIA_DIR
the media folder within the addon directory

*_MAP_FILENAME
dictionary file for converting Yomichan term/reading
pairs into audio file information
"""

JPOD_SOURCE_PARAM = "jpod"
JPOD_PATH = "jpod_audio"
JPOD_MEDIA_DIR = "user_files/jpod_files"
JPOD_MAP_FILENAME = "jpod_map.json"

JPOD_ALTERNATE_SOURCE_PARAM = "jpod_alternate"
JPOD_ALTERNATE_PATH = "jpod_alternate_audio"
JPOD_ALTERNATE_MEDIA_DIR = "user_files/jpod_alternate_files"
JPOD_ALTERNATE_MAP_FILENAME = "jpod_alternate.json"

NHK16_SOURCE_PARAM = "nhk16"
NHK16_PATH = "nhk16_audio"
NHK16_MEDIA_DIR = "user_files/nhk16_files"
NHK16_MAP_FILENAME = "nhk16_map.json"

"""
Maps set to global variables in order to
prevent reloading on each request
"""
JPOD_MAP = defaultdict(list)
JPOD_ALTERNATE_MAP = defaultdict(list)
NHK16_MAP = {}

def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

def remove_prefix(input_string, prefix):
    if prefix and input_string.startswith(prefix):
        return input_string[len(prefix):]
    return input_string

def get_program_root_path():
    dirname = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")
    if dirname.endswith("/"):
        return dirname[:-1]
    return dirname

def find_file(filename, relative_path):
    if not relative_path.startswith("/"):
        relative_path = "/" + relative_path
    path = get_program_root_path() + relative_path
    for root, _, files in os.walk(path):
        if filename in files:
            return os.path.join(root, filename)
    return None

def load_jpod_map():
    map_file = find_file(JPOD_MAP_FILENAME, "/")
    if not map_file:
        audio_dict = defaultdict(list)
        start = get_program_root_path() + "/" + JPOD_MEDIA_DIR
        for root, _, files in os.walk(start, topdown=False):
            for name in files:
                if not name.endswith('.mp3'):
                    continue
                parts = remove_suffix(name, '.mp3').split(" - ")
                if len(parts) != 2:
                    continue
                path = os.path.join(root, name)
                relative_path = os.path.relpath(path, start)
                audio_dict[f"{parts[0]} - {parts[1]}"] += [relative_path]
                audio_dict[parts[0]] += [relative_path]

        map_file = get_program_root_path() + "/" + JPOD_MAP_FILENAME
        with open(map_file, "w", encoding="utf-8", errors="ignore") as f:
            f.write(json.dumps(audio_dict, ensure_ascii=False, sort_keys=True))

    with open(map_file, "r", encoding="utf-8", errors="ignore") as f:
        return json.load(f)

def load_jpod_alternate_map():
    map_file = find_file(JPOD_ALTERNATE_MAP_FILENAME, "/")
    if not map_file:
        audio_dict = defaultdict(list)
        start = get_program_root_path() + "/" + JPOD_ALTERNATE_MEDIA_DIR
        for root, _, files in os.walk(start, topdown=False):
            for name in files:
                if not name.endswith('.mp3'):
                    continue
                parts = remove_suffix(name, '.mp3').split(" - ")
                if len(parts) != 2:
                    continue
                path = os.path.join(root, name)
                relative_path = os.path.relpath(path, start)
                audio_dict[f"{parts[0]} - {parts[1]}"] += [relative_path]
                audio_dict[parts[0]] += [relative_path]

        map_file = get_program_root_path() + "/" + JPOD_ALTERNATE_MAP_FILENAME
        with open(map_file, "w", encoding="utf-8", errors="ignore") as f:
            f.write(json.dumps(audio_dict, ensure_ascii=False, sort_keys=True))

    with open(map_file, "r", encoding="utf-8", errors="ignore") as f:
        return json.load(f)

def load_nhk16_map():
    map_file = find_file(NHK16_MAP_FILENAME, "/")
    if not map_file:
        entries_file = find_file("entries.json", NHK16_MEDIA_DIR)
        if not entries_file:
            return {}
        map_file = get_program_root_path() + "/" + NHK16_MAP_FILENAME
        make_nhk16_map(entries_file, map_file)
    with open(map_file, "r", encoding="utf-8", errors="ignore") as f:
        return json.load(f)


class AccentHandler(http.server.SimpleHTTPRequestHandler):
    def log_error(self, *args, **kwargs):
        """By default, SimpleHTTPRequestHandler logs to stderr.  This would
        cause Anki to show an error, even on successful requests
        log_error is still a useful function though, so replace it
        with the inherited log_message."""
        super().log_message(*args, **kwargs)

    def log_message(self, *args):
        """Make log_message do nothing."""
        pass

    def get_jpod_sources(self, term, reading):
        global JPOD_MAP
        audio_sources = []
        if len(JPOD_MAP) == 0:
            JPOD_MAP = load_jpod_map()
        files = JPOD_MAP.get(f"{reading} - {term}")
        if files:
            for file in files:
                audio_sources += [{"name": "JPod101 (Exact)",
                                   "url": f"http://{HOSTNAME}:{PORT}/{JPOD_PATH}/{quote(file)}"}]
        if len(audio_sources) > 0:
            return audio_sources
        files = JPOD_MAP.get(reading)
        if files:
            for file in files:
                audio_sources += [{"name": "JPod101 (Reading)",
                                   "url": f"http://{HOSTNAME}:{PORT}/{JPOD_PATH}/{quote(file)}"}]
        return audio_sources

    def get_jpod_alternate_sources(self, term, reading):
        global JPOD_ALTERNATE_MAP
        audio_sources = []
        if len(JPOD_ALTERNATE_MAP) == 0:
            JPOD_ALTERNATE_MAP = load_jpod_alternate_map()
        files = JPOD_ALTERNATE_MAP.get(f"{reading} - {term}")
        if files:
            for file in files:
                audio_sources += [{"name": "JPod101 Alternate (Exact)",
                                   "url": f"http://{HOSTNAME}:{PORT}/{JPOD_ALTERNATE_PATH}/{quote(file)}"}]
        if len(audio_sources) > 0:
            return audio_sources
        files = JPOD_ALTERNATE_MAP.get(reading)
        if files:
            for file in files:
                audio_sources += [{"name": "JPod101 Alternate (Reading)",
                                   "url": f"http://{HOSTNAME}:{PORT}/{JPOD_ALTERNATE_PATH}/{quote(file)}"}]
        return audio_sources

    def get_nhk16_sources(self, term, reading):
        global NHK16_MAP
        audio_sources = []
        if len(NHK16_MAP) == 0:
            NHK16_MAP = load_nhk16_map()
        if term in NHK16_MAP:
            for value in NHK16_MAP[term]:
                audio_sources += [{"name": value[0],
                                   "url": f"http://{HOSTNAME}:{PORT}/{NHK16_PATH}/{value[1]}"}]
        elif reading in NHK16_MAP:
            for value in NHK16_MAP[reading]:
                audio_sources += [{"name": value[0],
                                   "url": f"http://{HOSTNAME}:{PORT}/{NHK16_PATH}/{value[1]}"}]
        return audio_sources

    def get_jpod_audio(self):
        audio_file = get_program_root_path() + \
            f"/{JPOD_MEDIA_DIR}/" + \
            remove_prefix(unquote(self.path), f"/{JPOD_PATH}/")
        if not Path(audio_file).is_file() or not audio_file.endswith(".mp3"):
            self.send_response(400)
            return
        self.send_response(200)
        self.send_header('Content-type', 'text/mpeg')
        self.end_headers()
        with open(audio_file, 'rb') as fh:
            self.wfile.write(fh.read())

    def get_jpod_alternate_audio(self):
        audio_file = get_program_root_path() + \
            f"/{JPOD_ALTERNATE_MEDIA_DIR}/" + \
            remove_prefix(unquote(self.path), f"/{JPOD_ALTERNATE_PATH}/")
        if not Path(audio_file).is_file() or not audio_file.endswith(".mp3"):
            self.send_response(400)
            return
        self.send_response(200)
        self.send_header('Content-type', 'text/mpeg')
        self.end_headers()
        with open(audio_file, 'rb') as fh:
            self.wfile.write(fh.read())

    def get_nhk16_audio(self):
        filename = unquote(self.path).split("/")[-1]
        audio_file = find_file(filename, NHK16_MEDIA_DIR)
        if not audio_file:
            self.send_response(400)
            return
        self.send_response(200)
        self.send_header('Content-type', 'audio/aac')
        self.end_headers()
        with open(audio_file, 'rb') as fh:
            self.wfile.write(fh.read())

    def parse_query_components(self):
        """Extract 'term', 'reading', and 'sources' query parameters"""
        query_components = parse_qs(urlparse(self.path).query)
        term = query_components["term"][0] if "term" in query_components else ""
        if term == "":
            # Yomichan used to use "expression" but renamed to term.
            # Still support "expression" for older versions
            term = query_components["expression"][0] if "expression" in query_components else ""
        reading = query_components["reading"][0] if "reading" in query_components else ""
        sources = query_components["sources"][0].split(',') if "sources" in query_components else [JPOD_SOURCE_PARAM, JPOD_ALTERNATE_SOURCE_PARAM, NHK16_SOURCE_PARAM]
        return term, reading, sources

    def do_GET(self):
        if self.path.startswith(f"/{JPOD_PATH}/"):
            self.get_jpod_audio()
            return
        elif self.path.startswith(f"/{JPOD_ALTERNATE_PATH}/"):
            self.get_jpod_alternate_audio()
            return
        elif self.path.startswith(f"/{NHK16_PATH}/"):
            self.get_nhk16_audio()
            return

        term, reading, sources = self.parse_query_components()

        audio_sources = []
        for source in sources:
            if source == JPOD_SOURCE_PARAM:
                audio_sources += self.get_jpod_sources(term, reading)
            elif source == JPOD_ALTERNATE_SOURCE_PARAM:
                audio_sources += self.get_jpod_alternate_sources(term, reading)
            elif source == NHK16_SOURCE_PARAM:
                audio_sources += self.get_nhk16_sources(term, reading)

        # Build JSON that yomichan requires
        # Ref: https://github.com/FooSoft/yomichan/blob/master/ext/data/schemas/custom-audio-list-schema.json
        resp = {
            "type": "audioSourceList",
            "audioSources": audio_sources
        }

        # Writing the JSON contents with UTF-8
        payload = bytes(json.dumps(resp), "utf8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-length", str(len(payload)))
        self.end_headers()
        try:
            self.wfile.write(payload)
        except BrokenPipeError:
            self.log_error("BrokenPipe when sending reply")
        return


if __name__ == "__main__":
    # If we're not in Anki, run the server directly and blocking for easier debugging
    print("Running in debug mode...")
    httpd = socketserver.TCPServer((HOSTNAME, PORT), AccentHandler)
    httpd.serve_forever()
else:
    # Else, run it in a separate thread so it doesn't block
    httpd = http.server.ThreadingHTTPServer((HOSTNAME, PORT), AccentHandler)
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
