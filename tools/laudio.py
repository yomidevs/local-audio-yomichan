"""
An internal CLI script to play and add audio from the local server.
Maybe this can be an add-on (or part of this one) later?

Requirements:
- requests library (`pip install requests`)
- mpv
- 'anki' command:
    - Anki-Connect (with Anki open)

Usage:

`anki` command:
    - attempts to find a unique card
    - gets reading from the word reading field
`current` command:
    - equivalent of `anki`, but uses the current card as shown on the reviewer screen.
`play` command:
    - directly queries the server with the word (and optionally, reading)
    - cannot add the result to any card, can only play

Usage (audio selector):

> 0
    - play the audio at index 0
> 3
    - play the audio at index 3
> a
    - adds the audio with index 0 to the card (if `anki` or `current`)
> a3
    - adds the audio with index 3 to the card (if `anki` or `current`)
> e
    - exit

"""

import re
import sys
import json
import shlex
import argparse
import subprocess
import configparser
import urllib.request

from pathlib import Path
from time import localtime, strftime
from urllib.parse import urlparse
from typing import Any

import requests


rx_PLAIN_FURIGANA = re.compile(r" ?([^ >]+?)\[(.+?)\]")


# taken from https://github.com/FooSoft/anki-connect#python
def request(action: str, **params):
    return {"action": action, "params": params, "version": 6}


def invoke(action: str, **params):
    requestJson = json.dumps(request(action, **params)).encode("utf-8")
    response = json.load(
        urllib.request.urlopen(
            urllib.request.Request("http://127.0.0.1:8765", requestJson)
        )
    )
    if len(response) != 2:
        raise Exception("response has an unexpected number of fields")
    if "error" not in response:
        raise Exception("response is missing required error field")
    if "result" not in response:
        raise Exception("response is missing required result field")
    if response["error"] is not None:
        raise Exception(response["error"])
    return response["result"]


def get_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    anki = subparsers.add_parser("anki")
    anki.add_argument("word", type=str)
    anki.add_argument(
        "--key", action="store_true", help="search key instead of word field"
    )
    anki.add_argument(
        "--db-search",
        nargs=2,
        type=str,
        default=(None, None),
        help="search the specified word and reading instead",
    )

    current = subparsers.add_parser(
        "current", help="play currently displayed Anki card"
    )  # short for "anki current"
    current.add_argument(
        "--db-search",
        nargs=2,
        type=str,
        default=(None, None),
        help="search the specified word and reading instead",
    )

    play = subparsers.add_parser("play")
    play.add_argument("wordreading", type=str, nargs="+", action=required_length(1, 2))

    return parser.parse_args()


def get_global_config():
    config = configparser.ConfigParser()
    default_config = Path(__file__).parent.joinpath("default_config.ini")
    user_config = Path(__file__).parent.joinpath("config.ini")

    config.read(default_config)
    config.read(user_config)
    return dict(config["DEFAULT"])


def plain_to_kana(text: str):
    result = text.replace("&nbsp;", " ")
    return rx_PLAIN_FURIGANA.sub(r"\2", result)


def os_cmd(cmd):
    # shlex.split used for POSIX compatibility
    return cmd if sys.platform == "win32" else shlex.split(cmd)


def required_length(nmin: int, nmax: int):
    """
    taken from https://stackoverflow.com/a/4195302
    """

    class RequiredLength(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if not nmin <= len(values) <= nmax:
                msg = 'argument "{f}" requires between {nmin} and {nmax} arguments'.format(
                    f=self.dest, nmin=nmin, nmax=nmax
                )
                raise argparse.ArgumentTypeError(msg)
            setattr(args, self.dest, values)

    return RequiredLength


def parse_args(args, config) -> tuple[str | None, str | None, int | None]:
    """
    gets word, reading, and note_id from args
    """
    command = args.command
    note_id = None

    word_field = config["word_field"]
    reading_field = config["reading_field"]

    if command == "anki" or command == "current":
        if command == "anki":
            search_field = config["key_field"] if args.key else config["word_field"]
            note_type = config["note_type"]

            note_ids = invoke(
                "findNotes", query=f'"note:{note_type}" "{search_field}:{args.word}"'
            )
            notes_info = invoke("notesInfo", notes=note_ids)
            if len(note_ids) > 1:
                print("Multiple cards found!")
                print([info["fields"]["Key"]["value"] for info in notes_info])
                return (None, None, None)
            if len(note_ids) < 1:
                print("No cards found!")
                return (None, None, None)

            note_id = note_ids[0]
            note_info = notes_info[0]
        else:  # current
            note_info = invoke("guiCurrentCard")
            note_id = invoke("cardsToNotes", cards=[note_info["cardId"]])[0]

        db_word, db_reading = args.db_search
        if db_word is None or db_reading is None:
            # use word from Anki
            word = note_info["fields"][word_field]["value"]
            word_reading = note_info["fields"][reading_field]["value"]
            reading = plain_to_kana(word_reading)
        else:
            # we search the database with the field
            word = db_word
            reading = db_reading

        print(word, reading)

    else:  # play
        # can be 1+ args
        if len(args.wordreading) == 1:
            word = args.wordreading[0]
            reading = None
        else:  # len == 2
            word, reading = args.wordreading

    return word, reading, note_id


class AudioPlayer:
    def __init__(
        self,
        word: str,
        reading: str | None,
        note_id: int | None,
        config: dict[str, Any],
    ):
        self.word = word
        self.reading = reading
        self.note_id = note_id
        self.sources = self.get_sources()
        self.config = config

    def send_audio(self, url: str):
        suffix = url[url.rfind(".") :]
        source = Path(urlparse(url).path).parts[
            1
        ]  # crazy hack to get the top most directory

        file_name = (
            f"local_audio_{source}_{self.word}_{self.reading}_"
            + strftime("%Y-%m-%d-%H-%M-%S", localtime())
            + suffix
        )
        print(file_name)

        audio_data = [{"url": url, "filename": file_name, "fields": ["WordAudio"]}]

        invoke(
            "updateNoteFields",
            note={
                "id": self.note_id,
                "fields": {
                    "WordAudio": "",
                },
                "audio": audio_data,
            },
        )

    def pretty_print_sources(self, sources):
        for i, source in enumerate(sources):
            print("", i, source["name"])

    def get_sources(self):
        if self.reading is None:
            query_url = f"http://localhost:5050/?term={self.word}"
        else:
            query_url = (
                f"http://localhost:5050/?term={self.word}&reading={self.reading}"
            )
        r = requests.get(query_url)
        sources = r.json().get("audioSources")
        return sources

    def play_audio(self, url: str):
        temp_audio_path = Path(__file__).parent.joinpath("temp_audio")

        r = requests.get(url)
        with open(temp_audio_path, "wb") as f:
            f.write(r.content)

        mpv_path = self.config["mpv_path"]

        subprocess.run(os_cmd(f"{mpv_path} {temp_audio_path}"), encoding="utf8")

    def run_main_loop(self):
        if len(self.sources) == 0:
            print(f"No sources found for ({self.word}, {self.reading}). Exiting...")
            return

        while True:
            print()
            self.pretty_print_sources(self.sources)
            print()

            user_input = input("> ").strip()
            if user_input == "e":
                return
            elif user_input == "":
                pass
            elif user_input.startswith("a"):  # add audio
                if user_input == "a":
                    idx = 0
                else:
                    idx = int(user_input[1:])

                if 0 <= idx < len(self.sources):
                    url = self.sources[idx]["url"]
                else:
                    print(f"Invalid index: {idx}")
                    continue

                assert self.note_id is not None
                self.send_audio(url)
                return

            else:  # play audio
                idx = int(user_input)

                if 0 <= idx < len(self.sources):
                    url = self.sources[idx]["url"]
                else:
                    print(f"Invalid index: {idx}")
                    continue

                print(url)
                self.play_audio(url)


def main():
    config = get_global_config()
    args = get_args()
    word, reading, note_id = parse_args(args, config)
    # TODO: accept either word is None or reading is None
    if word is None:
        return
    player = AudioPlayer(word, reading, note_id, config)
    player.run_main_loop()


if __name__ == "__main__":
    main()
