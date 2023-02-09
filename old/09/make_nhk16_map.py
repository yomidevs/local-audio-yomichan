import json

num2fullwidth = str.maketrans("0123456789", "０１２３４５６７８９")
num_map = {0: "零", 1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七", 8: "八", 9: "九", 10: "十", 11: "十一", 12: "十二", 13: "十三", 14: "十四", 15: "十五", 16: "十六", 17: "十七", 18: "十八", 19: "十九", 20: "二十", 21: "二十一", 22: "二十二", 23: "二十三", 24: "二十四", 25: "二十五", 26: "二十六", 27: "二十七", 28: "二十八", 29: "二十九", 30: "三十", 31: "三十一", 32: "三十二", 33: "三十三", 34: "三十四", 35: "三十五", 36: "三十六", 37: "三十七", 38: "三十八", 39: "三十九", 40: "四十", 41: "四十一", 42: "四十二", 43: "四十三", 44: "四十四", 45: "四十五", 46: "四十六", 47: "四十七", 48: "四十八", 49: "四十九", 50: "五十", 51: "五十一", 52: "五十二", 53: "五十三", 54: "五十四", 55: "五十五", 56: "五十六", 57: "五十七", 58: "五十八", 59: "五十九", 60: "六十", 61: "六十一", 62: "六十二", 63: "六十三", 64: "六十四", 65: "六十五", 66: "六十六", 67: "六十七", 68: "六十八", 69: "六十九", 70: "七十", 71: "七十一", 72: "七十二", 73: "七十三", 74: "七十四", 75: "七十五", 76: "七十六", 77: "七十七", 78: "七十八", 79: "七十九", 80: "八十", 81: "八十一", 82: "八十二", 83: "八十三", 84: "八十四", 85: "八十五", 86: "八十六", 87: "八十七", 88: "八十八", 89: "八十九", 90: "九十", 91: "九十一", 92: "九十二", 93: "九十三", 94: "九十四", 95: "九十五", 96: "九十六", 97: "九十七", 98: "九十八", 99: "九十九", 100: "百", 1000: "千", 10000: "一万"}


def get_numbers(number):
    if number == "何［ナン］":
        return ["何", "ナン", "なん"]
    return [f"{number}".translate(num2fullwidth), num_map[int(number)]]


def append_to(output, key, value):
    if key not in output:
        output[key] = []
    if value not in output[key]:
        output[key].append(value)


def get_clean_kanji(dirty_kanji):
    clean_kanji = []
    for kanji in dirty_kanji:
        for x in kanji.split("，"):
            y = x.strip()
            if y != "":
                clean_kanji.append(y)
    return clean_kanji


def get_accent_data(accent):
    sound_file = accent["soundFile"]
    if sound_file is None:
        return None
    display_text = ""
    for word_segment in accent["accent"]:
        pronunciation = word_segment["pronunciation"]
        pitch_accent = word_segment["pitchAccent"]
        display_text += f"{pronunciation}[{pitch_accent}]"
    return [display_text, sound_file]


def get_pronunciation(accent):
    pronunciation = ""
    for word_segment in accent["accent"]:
        pronunciation += word_segment["pronunciation"]
    return pronunciation


def make_nhk16_map(entries_file, map_file):
    output = {}

    with open(entries_file, "r", encoding="utf-8", errors="ignore") as f:
        entries = json.load(f)

    for entry in entries:
        kana = entry["kana"]
        kanji_list = get_clean_kanji(entry["kanji"])

        optional_kanji_list = get_clean_kanji(entry["kanjiNotUsed"])
        for optional_kanji in optional_kanji_list:
            for kanji in kanji_list:
                if optional_kanji in kanji:
                    kanji_list.remove(kanji)

        for accent in entry["accents"]:
            accent_data = get_accent_data(accent)
            if accent_data is None:
                continue
            append_to(output, kana, accent_data)
            for kanji in kanji_list:
                append_to(output, kanji, accent_data)

        for subentry in entry["subentries"]:
            if "head" in subentry:
                head = subentry["head"]
                for accent in subentry["accents"]:
                    accent_data = get_accent_data(accent)
                    if accent_data is None:
                        continue
                    append_to(output, head, accent_data)
            else:  # number (+counter) section
                numbers = get_numbers(subentry["number"])
                for accent in subentry["accents"]:
                    accent_data = get_accent_data(accent)
                    if accent_data is None:
                        continue
                    pronunciation = get_pronunciation(accent)
                    append_to(output, pronunciation, accent_data)
                    for kanji in kanji_list:
                        if kanji == "整数":
                            continue  # plain integer section
                        for number in numbers:
                            append_to(output, f"{number}{kanji}", accent_data)
                    for number in numbers:
                        append_to(output, f"{number}{kana}", accent_data)
                continue

    with open(map_file, "w", encoding="utf-8", errors="ignore") as f:
        f.write(json.dumps(output, ensure_ascii=False, sort_keys=True))
