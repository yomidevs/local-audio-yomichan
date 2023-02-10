
# Local Audio Server for Yomichan

This is a completely optional setup for people who want to be
able to create Anki cards nearly instantaneously, and without
a working internet connection.


<details>
<summary>Reasons for and against using this setup <i>(click here)</i></summary>


* **Advantages:**

    1. Most audio is gotten in **less than a second**. Without the local audio server,
        fetching the audio can take anywhere from three seconds to a full minute
        (on particularly bad days).

        Most of the delay from Yomichan when creating cards is from fetching the audio.
        In other words, getting the audio is the main bottleneck of when creating Anki cards.
        This setup removes this bottleneck, and allows you to make cards **nearly instaneously**.

    1. If you do not have internet access, you can still add audio to your cards.

* **Disadvantages:**

    1. This setup requires about **5GB of free space**.

    1. It only has the coverage of JPod 101, NHK16 and select audio from Forvo
        (which is still about 99% coverage, from personal experience).
        To increase audio coverage,
        it would be ideal to also include an extra
        [Forvo audio source](https://learnjapanese.moe/yomichan/#bonus-adding-forvo-extra-audio-source).

</details>


<details> <summary>Notes on Forvo Audio Sourcing <i>(click here)</i></summary>

* The following is a slightly edited quote from person who got the Forvo audio:

    > The files for now only includes audio files with an exact 1:1 mapping of a dictionary/Marv's JPDB frequency list term to the name of the file the user uploaded. Just because you don't get audio for an user it does not mean the user has no audio on Forvo. Just because you get audio it does not mean it actually matches the current word/reading. It is also not uncommon that people pronounce multiple readings in the same file.

    The full quote can be found at the bottom of the page, under "Original Message for v09".

</details>

<sup>
P.S. Feel free to check out <a href="https://aquafina-water-bottle.github.io/jp-mining-note/jpresources/">my other resources</a> if you're interested!
</sup>

## Steps

These instructions only work on the PC release of Anki.
If you wish to use this on AnkiDroid, see [here](https://github.com/KamWithK/AnkiconnectAndroid).
There is currently no way of using this on AnkiMobile.

1.  Download the add-on. (TODO link anki web)
    If you are using Anki versions 2.1.49 or below, I recommend updating Anki.
    If you can't do this for whatever reason, the legacy instructions and add-on can be found
    [here](https://github.com/Aquafina-water-bottle/local-audio-yomichan/tree/old).

1. Install the add-on by heading over to:

    > (Anki) →  `Tools` →  `Add-ons` →  `Install from file...`

1. Download all the required audio files.
    They can be found at this [torrent link](https://nyaa.si/view/1625597).

    <details> <summary>Magnet link <i>(click here)</i></summary>

        magnet:?xt=urn:btih:15f4557bc3e5464609bc1f9ac444db3611b97541&dn=Yomichan%20Japanese%20Local%20Audio%20-%20JapanesePod101%20%28JPod%29%2C%20NHK%2C%20Forvo%20Select%20Users&tr=http%3A%2F%2Fnyaa.tracker.wf%3A7777%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce

    </details>

1. Place the audio files under `Anki2/addons21/955441350/user_files`.
    See [Anki's documentation](https://docs.ankiweb.net/files.html#file-locations)
    on instructions to find your `Anki2` folder.

    <details> <summary>Expected file structure <i>(click here)</i></summary>

        955441350
        └── user_files
            ├── forvo_files
            │   ├── akitomo
            │   │   └── 目的.mp3
            │   ├── kaoring
            │   │   └── ...
            │   └── ...
            ├── jpod_alternate_files
            │   ├── よむ - 読む.mp3
            │   └── ...
            ├── jpod_files
            │   ├── よむ - 読む.mp3
            │   └── ...
            └── nhk16_files
                ├── audio
                │   ├── 20170616125910.aac
                │   └── ...
                └── entries.json

    </summary>

1. In Yomichan Settings, go to:

    > `Audio` →  `Configure audio playback sources`.

    Click `Add`, and set the source to be `Add Custom URL (JSON)`.

    Set the `URL` field to:
    ```
    http://localhost:5050/?sources=jpod,jpod_alternate,nhk16,forvo&term={term}&reading={reading}
    ```

1. Restart Anki.

    Because restarting Anki will generate the database file,
    it may appear that Anki is not loading.
    This is normal, and expect this to take a while.

1. Ensure that everything works. To do this, play some audio from Yomichan.
    You should notice two things:

    - The audio should be played almost immediately after clicking the play button.
        Note that if you're using the memory based version,
        the first audio play will take a while to load as mentioned above (in the comparison).
    - After playing the audio, you should be able to see the available sources
        by right-clicking on the play button.

        Here is an example for 読む:

        ![image](./img/yomu.gif)

    Play all the sources from the above (読む) to ensure the sound is properly fetched.

    > **Note**: If some sources don't work, try regenerating the database
    > by navigating to `Tools` →  `Regenerate local audio database`.


## Usage Notes

* The local audio server only works when Anki is open. Of course, it can be running minimized in the background.

* The sources can be rearranged to give priority to a different source.
    For example, if you want Forvo to have the highest priority, use
    `sources=forvo,jpod,jpod_alternate,nhk16`
    (under the Custom URL step).

* For Forvo audio specifically, you can modify the priority of users by using `&user=`.

    For example, the following will get forvo audio in the priority of strawberrybrown, then akitomo. All other users **will not be included in the search**.
    ```
    http://localhost:5050/?sources=jpod,jpod_alternate,nhk16,forvo&term={term}&reading={reading}&user=strawberrybrown,akitomo
    ```

## Credits & Acknowledgements
* **`Zetta#3033`**: Creator of the original addon + advice for improving query speed
* **`kezi#0001`**: Getting NHK16 audio
* **`(anonymous)`**: Adding SQL + NHK16 audio support
* **`Renji-xD#8182`**: Getting Forvo audio, adding Forvo audio support
* **`Marv#5144`**: Creating and maintaining the torrent
* **`shoui 🐈#0520`**: Maintaining and popularizing the original set of instructions that these instructions were initially based off of
* **`jamesnicolas`**: Creator of [yomichan-forvo-server](https://github.com/jamesnicolas/yomichan-forvo-server). The original code was heavily based off of this project.
* **`KamWithK`**: Creator of [Ankiconnect Android](https://github.com/KamWithK/AnkiconnectAndroid). This allows the local audio server to work on Android.
* **`Aquafina water bottle`**: Everything else (Merged SQL + forvo audio versions, implemented faster SQL lookups, rewrote codebase, etc.)


## License
[MIT](https://github.com/Aquafina-water-bottle/local-audio-yomichan/blob/master/LICENSE)

## Original Messages

<details> <summary>Original Message for v01 <i>(click here)</i></summary>

<sup>
<a href="https://discord.com/channels/617136488840429598/778430038159655012/943743205931900928">Original discord message</a>, on
<a href="https://learnjapanese.moe/join/">TMW server</a>
</sup>

> Zetta — 16/02/2022 <br>
> Yomichan Local Audio Server Anki Plugin V0.1 (probably buggy) This plugin acts similar to the Forvo Audio Server plugin but runs off the downloaded JapanesePod audio files. The purpose is to provide offline access and faster look ups for audio that exists in the dump.
> 
> Any audio files with the format of `<reading> - <term>.mp3` under the plugins `user_files` directory will be used. Folder structure under `user_files` doesn’t matter. For example `よむ - 読む.mp3` it will try to match the yomichan entry to both reading and term and show up as `Local (Exact)` Failing that, it will just use `reading` and show up as `Local (Reading)` in the yomichan audio dropdown.
> 
> How to use:
> 
> 1. Install the attached addon like any other local addon.
> 1. Restart Anki
> 1. Allow network connections (required since this is a local server)
> 1. In yomichan settings, go to Audio > Configure Audio Playback Sources > Custom Audio Source
> 1. Select Type as JSON and set URL to `http://localhost:5050/?term={term}&reading={reading}`
> 1. Download the JapansePod Audio dump from here https://discord.com/channels/617136488840429598/778430038159655012/943679275884740608 and unzip all archives it in your Anki2 folder under `addons21/955441350/user_files`
> 1. (You may need to Restart Anki again if it doesn’t start working.)
> 
> Bugfix for multiple files named the same in different directories under user_files. https://discord.com/channels/617136488840429598/778430038159655012/943876430746513429 <br>
> Credit: Much of the code was ripped from https://github.com/jamesnicolas/yomichan-forvo-server

</details>


<details> <summary>Original Message for v09 <i>(click here)</i></summary>

<sup>
<a href="https://discord.com/channels/617136488840429598/778430038159655012/1047979092777123950">Original discord message</a>, on
<a href="https://learnjapanese.moe/join/">TMW server</a>
</sup>

> 猫です — 01/12/2023 <br>
> experimental extension of the local yomichan server with forvo users akitomo, kaoring, poyotan, skent, strawberrybrown (only tested for couple of minutes on a windows machine so lets hope for the best)
> 
> https://mega.nz/folder/1XgGgSBZ#_rQZLbxS5EcEv68S9I_WAw
> 
> Follow https://github.com/Aquafina-water-bottle/jmdict-english-yomichan/tree/master/local_audio#steps to install option 1 of the local audio addon in anki.
> Extract localaudio_v09.zip into the main addon folder of anki (you can rename the init.py file in case you want a backup, otherwise just overwrite)
> Extract contents of forvo_files_v09.zip to user_files/forvo_files (so that you have 5 folders named after the mentioned users)
> Restart and reopen Anki
> 
> Add forvo as value to the source parameter for the playback source in yomichan: e. g. `http://localhost:5050/?sources=forvo,jpod,jpod_alternate,nhk16&term={term}&reading={reading}`
> 
> You can add an user parameter to modify the sort order/which users should be displayed/used (nothing found means nothing displayed for forvo): e. g. `http://localhost:5050/?sources=forvo,jpod,jpod_alternate,nhk16&term={term}&reading={reading}&user=strawberrybrown,akitomo` (in case there is no audio for strawberrybrown/akitomo but poyotan have one still nothing would be displayed)
> 
> Note: maybe you saw the discussion - the files for now only includes  audio files with an exact 1:1 mapping of a dictionary/marvs jpdb frequency list term to the name of the file the user uploaded. Just because you don't get audio for an user it does not mean the user has no audio on forvo. Just because you get audio it does not mean it actually matches the current word/reading (also not uncommon that people pronounce multiple readings in the same file). Maybe one day me or someone find a nice way to normalize the filenames and is in the mood to extend the script/files for better results/accuracy but for now you need to live with what you get : >

</details>

<details> <summary>Original message for vsql_09 hotfix (2023_01_15 -> 2023_01_24) <i>(click here)</i></summary>

<sup>
<a href="https://discord.com/channels/617136488840429598/778430038159655012/1067694392393093220">Original discord message</a>, on
<a href="https://learnjapanese.moe/join/">TMW server</a>
</sup>

> Aquafina water bottle — 01/24/2023 <br>
> Out of pure stupidity, the jpod_alternate audio files aren't actually found in the `sql_09` version. If you already have it installed, here's how to hotfix it:
> 1. Download the new `__init__.py` file. You can find it in the zip below or at this link: https://raw.githubusercontent.com/Aquafina-water-bottle/jmdict-english-yomichan/master/local_audio/sql_09/__init__.py
> 2. Navigate to `Anki2/addons21/955441350`
> 3. Replace the `__init__.py` file with the one downloaded from step 1.
> 4. Remove the `entries.db` file entirely.
> 5. Restart Anki. You should now be able to see 読む from all 4 sources. It should look like step 7 from the standard setup instructions: <https://github.com/Aquafina-water-bottle/jmdict-english-yomichan/tree/master/local_audio>
> 
> Worst case scenario, if the hotfix doesn't work, it's likely best to just re-do the setup process from scratch by deleting the addon and following the steps in the README. Make sure you save the `user_files` folder so you don't have to re-download any audio files.

</details>

