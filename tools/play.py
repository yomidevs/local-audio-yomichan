"""
An internal CLI script to play and add audio from the local server.
Maybe this can be an add-on (or part of one) later?

Requirements:
- requests library (`pip install requests`)
- mpv
- 'anki' command:
    - Anki-Connect (with Anki open)

WARNING:
- Hard coded to use "JP Mining Note" (TODO: make configurable)
- Requires *nix systems (as `/tmp/` and `mpv` is hard coded) (TODO: make configurable)

Usage:

`anki` command:
    - attempts to find a unique card
    - gets reading from WordReading
`current` command:
    - equivalent of `anki`, but uses the current card as shown on the reviewer screen.
`local` command:
    - directly queries the server with the word and reading
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
import urllib
import argparse
import subprocess
from time import localtime, strftime

import requests



rx_PLAIN_FURIGANA = re.compile(r" ?([^ >]+?)\[(.+?)\]")



# taken from https://github.com/FooSoft/anki-connect#python
def request(action: str, **params):
    return {"action": action, "params": params, "version": 6}


def invoke(action: str, **params):
    requestJson = json.dumps(request(action, **params)).encode("utf-8")
    response = json.load(
        urllib.request.urlopen(
            urllib.request.Request("http://localhost:8765", requestJson)
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
    subparsers = parser.add_subparsers(dest='command')

    anki = subparsers.add_parser("anki")
    anki.add_argument("word", type=str)
    anki.add_argument("--key", action="store_true", help="search key instead of word field")

    local = subparsers.add_parser("local")
    local.add_argument("word", type=str)
    local.add_argument("reading", type=str)

    subparsers.add_parser("current") # anki current

    return parser.parse_args()

def plain_to_kana(text: str):
    result = text.replace("&nbsp;", ' ')
    return rx_PLAIN_FURIGANA.sub(r"\2", result)

def os_cmd(cmd):
    # shlex.split used for POSIX compatibility
    return cmd if sys.platform == "win32" else shlex.split(cmd)


def send_audio(url: str, note_id: int, word: str, reading: str):
    suffix = url[url.rfind("."):]
    print(suffix)

    file_name = f"local_audio_{word}_{reading}_" + strftime("%Y-%m-%d-%H-%M-%S", localtime()) + suffix
    print(file_name)

    audio_data = [{
        "url": url,
        "filename": file_name,
        "fields": [
            "WordAudio"
        ]
    }]

    invoke("updateNoteFields", note={
        "id": note_id,
        "fields": {
            "WordAudio": "",
        },
        "audio": audio_data
    })


def pretty_print_sources(sources):
    for i, source in enumerate(sources):
        print("", i, source["name"])


def main():
    args = get_args()
    command = args.command
    note_id = None

    if command == "anki":
        field = "Key" if args.key else "Word"
        note_ids = invoke("findNotes", query=f'"note:JP Mining Note" "{field}:{args.word}"')
        notes_info = invoke("notesInfo", notes=note_ids)
        if len(note_ids) > 1:
            print("Multiple cards found!")
            print([info["fields"]["Key"]["value"] for info in notes_info])
            return
        if len(note_ids) < 1:
            print("No cards found!")
            return

        note_id = note_ids[0]
        note_info = notes_info[0]
        word_reading = note_info["fields"]["WordReading"]["value"]

        word = note_info["fields"]["Word"]["value"]
        reading = plain_to_kana(word_reading)

        print(word, reading)

    elif command == "current":
        note_info = invoke("guiCurrentCard")
        word_reading = note_info["fields"]["WordReading"]["value"]

        word = note_info["fields"]["Word"]["value"]
        reading = plain_to_kana(word_reading)
        note_id = invoke("cardsToNotes", cards=[note_info["cardId"]])[0]

        print(word, reading)

    else: # local
        word = args.word
        reading = args.reading


    r = requests.get(f'http://localhost:5050/?term={word}&reading={reading}')

    sources = r.json().get("audioSources")

    exit_loop = False
    while not exit_loop:
        print()
        pretty_print_sources(sources)
        print()

        user_input = input("> ").strip()
        try:
            if user_input == "e":
                exit_loop = True
            elif user_input == "":
                pass
            elif user_input.startswith("a"): # add audio
                if user_input == "a":
                    idx = 0
                else:
                    idx = int(user_input[1:])

                if 0 <= idx < len(sources):
                    url = sources[idx]["url"]
                else:
                    print(f"Invalid index: {idx}")
                    continue

                assert note_id is not None
                send_audio(url, note_id, word, reading)
                exit_loop = True

            else: # play audio
                idx = int(user_input)

                if 0 <= idx < len(sources):
                    url = sources[idx]["url"]
                else:
                    print(f"Invalid index: {idx}")
                    continue

                print(url)
                r2 = requests.get(url)
                with open("/tmp/local_audio", "wb") as f:
                    f.write(r2.content)

                subprocess.run(os_cmd("mpv /tmp/local_audio"), encoding="utf8")
        except Exception as e:
            #print(e)
            raise e


if __name__ == "__main__":
    main()

