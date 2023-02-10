from __future__ import annotations

import os
import http.server
import socketserver
import json
import sqlite3
import threading

from http import HTTPStatus
from urllib.parse import unquote
from urllib.parse import urlparse
from urllib.parse import parse_qs
from pathlib import Path

from .util import HOSTNAME, PORT, QueryComponents, get_db_path, get_program_root_path
from .all_sources import SOURCES, ID_TO_SOURCE_MAP



class LocalAudioHandler(http.server.SimpleHTTPRequestHandler):
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
        audio_file = os.path.join(
            get_program_root_path(),
            media_dir,
            file_path
        )
        if not Path(audio_file).is_file():
            self.send_response(400)
            return

        if audio_file.endswith(".mp3"):
            self.send_response(200)
            self.send_header("Content-type", "text/mpeg")
        elif audio_file.endswith(".aac"):
            self.send_response(200)
            self.send_header("Content-type", "text/aac")
        else:
            self.send_response(400)
            return

        self.end_headers()
        with open(audio_file, "rb") as fh:
            self.wfile.write(fh.read())

    def parse_query_components(self) -> QueryComponents:
        """Extract 'term', 'reading', 'sources', and 'user' query parameters"""
        parsed_qcomps = parse_qs(urlparse(self.path).query)

        if "term" in parsed_qcomps:
            term = parsed_qcomps["term"][0]
        elif "expression" in parsed_qcomps:
            term = parsed_qcomps["expression"][0]
        else:
            raise Exception("Cannot find term or expression in query")

        if "reading" in parsed_qcomps:
            reading = parsed_qcomps["reading"][0]
        else:
            raise Exception("Cannot find reading in query")

        if "sources" in parsed_qcomps:
            sources = parsed_qcomps["sources"][0].split(",")
        else:
            sources = [s.data.id for s in SOURCES]

        if "user" in parsed_qcomps:
            user = [u.strip() for u in parsed_qcomps["user"][0].split(",")]
        else:
            user = []

        qcomps = QueryComponents(term, reading, sources, user)

        return qcomps

    def do_GET(self):
        # https://stackoverflow.com/questions/7894384/python-get-url-path-sections
        urlparse(self.path).netloc
        parse_result = urlparse(self.path)
        full_path = unquote(parse_result.path)

        path_parts = full_path.split("/", 2)
        if len(path_parts) == 3 and (source_id := path_parts[1]) in ID_TO_SOURCE_MAP:
            audio_source = ID_TO_SOURCE_MAP[source_id]
            file_path = path_parts[2]
            self.get_audio(audio_source.get_media_dir_path(), file_path)
            return

        qcomps = self.parse_query_components()

        audio_sources_json_list = []
        with sqlite3.connect(get_db_path()) as connection:
            cursor = connection.cursor()

            for source in qcomps.sources:
                audio_source = ID_TO_SOURCE_MAP.get(source, None)
                if audio_source is not None:
                    audio_sources_json_list += audio_source.get_sources(connection, qcomps)
            cursor.close()

        # Build JSON that yomichan requires
        # Ref: https://github.com/FooSoft/yomichan/blob/master/ext/data/schemas/custom-audio-list-schema.json
        resp = {"type": "audioSourceList", "audioSources": audio_sources_json_list}

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

    from .gui import init_gui
    init_gui()


if __name__ == "__main__":
    # If we're not in Anki, run the server directly and blocking for easier debugging
    print("Running in debug mode...")
    httpd = socketserver.TCPServer((HOSTNAME, PORT), LocalAudioHandler)
    httpd.serve_forever()

