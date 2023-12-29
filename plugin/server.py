from __future__ import annotations

import http.server
import json
import sqlite3
import threading
import os

from http import HTTPStatus
from urllib.parse import unquote
from urllib.parse import urlparse
from urllib.parse import parse_qs
from pathlib import Path

from .util import (
    QueryComponents,
    get_db_path,
    get_android_db_path,
    get_version_file_path,
)
from .consts import *
from .config import ALL_SOURCES
from .db_utils import execute_query



class LocalAudioHandler(http.server.SimpleHTTPRequestHandler):

    # TODO: maybe use mimetypes.guess_type?
    # https://docs.python.org/3/library/mimetypes.html
    SUFFIX_TO_MIME_TYPE = {
        ".mp3": "audio/mpeg",
        ".aac": "audio/aac",
        ".m4a": "audio/mp4",
        ".ogg": "audio/ogg",
        ".oga": "audio/ogg",
        ".opus": "audio/ogg",
        ".flac": "audio/flac",
    }

    def log_error(self, *args, **kwargs):
        """By default, SimpleHTTPRequestHandler logs to stderr.  This would
        cause Anki to show an error, even on successful requests
        log_error is still a useful function though, so replace it
        with the inherited log_message."""
        super().log_message(*args, **kwargs)

    def log_message(self, *args):
        """Make log_message do nothing."""
        pass

    def get_audio(self, media_dir, file_path):
        audio_file = media_dir.joinpath(file_path)
        if not audio_file.is_file():
            self.send_response(400)
            return

        mime_type = LocalAudioHandler.SUFFIX_TO_MIME_TYPE.get(audio_file.suffix, None)
        if mime_type is None:
            self.send_response(400)
            return
        self.send_response(200)
        self.send_header("Content-type", mime_type)
        self.send_header("Content-length", str(os.stat(audio_file).st_size))
        self.end_headers()

        with open(audio_file, "rb") as fh:
            self.wfile.write(fh.read())

    def _get_audio_android(self, source, file_path):
        """
        internal testing method, shouldn't be used outside of testing the android db
        """
        audio_file = Path(file_path)

        mime_type = LocalAudioHandler.SUFFIX_TO_MIME_TYPE.get(audio_file.suffix, None)
        if mime_type is None:
            self.send_response(400)
            return
        self.send_response(200)
        self.send_header("Content-type", mime_type)
        self.end_headers()

        android_db_path = get_android_db_path()
        with sqlite3.connect(android_db_path) as android_connection:
            android_cursor = android_connection.cursor()
            sql = """
            SELECT data FROM android WHERE file = :file AND source = :source
            """
            row = android_cursor.execute(
                sql, {"file": file_path, "source": source}
            ).fetchone()
            if row is None:
                self.send_response(400)
                return

            data = row[0]
            self.wfile.write(data)

            android_cursor.close()

    def parse_query_components(self) -> QueryComponents:
        """Extract 'term', 'reading', 'sources', and 'user' query parameters"""
        parsed_qcomps = parse_qs(urlparse(self.path).query)

        if "term" in parsed_qcomps:
            term = parsed_qcomps["term"][0]
        elif "expression" in parsed_qcomps:
            term = parsed_qcomps["expression"][0]
        else:
            raise Exception(f"Cannot find term or expression in query: {self.path}")

        # reading field should actually be optional, to query just for the term / expression
        if "reading" in parsed_qcomps:
            reading = parsed_qcomps["reading"][0]
        else:
            reading = None

        if "sources" in parsed_qcomps:
            sources = parsed_qcomps["sources"][0].split(",")
        else:
            sources = list(ALL_SOURCES.keys())

        if "user" in parsed_qcomps:
            user = [u.strip() for u in parsed_qcomps["user"][0].split(",")]
        else:
            user = []

        qcomps = QueryComponents(term, reading, sources, user)

        return qcomps

    def send_version(self):
        latest_version_file = get_version_file_path()
        with open(latest_version_file) as f:
            ver = f.read().strip()
        payload = f"Local Audio Server v{ver}".encode("utf-8")

        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=UTF-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        print("GET:", self.path)

        # https://stackoverflow.com/questions/7894384/python-get-url-path-sections
        parse_result = urlparse(self.path)
        full_path = unquote(parse_result.path)

        # returns version as plaintext
        if self.path.strip() == "/" or self.path.strip() == "":
            self.send_version()
            return

        if full_path.strip() == "/favicon.ico":
            # skip entirely
            self.send_response(400)
            return

        path_parts = full_path.split("/", 2)
        if len(path_parts) == 3 and (source_id := path_parts[1]) in ALL_SOURCES:
            audio_source = ALL_SOURCES[source_id]
            file_path = path_parts[2]
            self.get_audio(audio_source.get_media_dir_path(), file_path)
            # self._get_audio_android(audio_source.data.id, file_path)
            return

        qcomps = self.parse_query_components()

        audio_sources_json_list = []
        with sqlite3.connect(get_db_path()) as connection:
            rows = execute_query(connection, qcomps)
            for row in rows:
                source = row[SOURCE]
                file = row[FILE]

                audio_source = ALL_SOURCES.get(source, None)
                if audio_source is None:
                    print(f"(do_GET) unknown source {source}")
                    continue

                # we use the %s substitutions so it's more compatible between other languages
                display = row[DISPLAY]
                if display is not None:
                    name = audio_source.data.display % row[DISPLAY]
                else:
                    name = audio_source.data.display
                url = audio_source.construct_file_url(file)
                entry = {"name": name, "url": url}
                audio_sources_json_list.append(entry)

        # Build JSON that Yomichan requires
        # Ref: https://github.com/FooSoft/yomichan/blob/master/ext/data/schemas/custom-audio-list-schema.json
        resp = {"type": "audioSourceList", "audioSources": audio_sources_json_list}
        print(audio_sources_json_list)

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


def run_server():
    # Else, run it in a separate thread so it doesn't block
    httpd = http.server.ThreadingHTTPServer((HOSTNAME, PORT), LocalAudioHandler)
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
