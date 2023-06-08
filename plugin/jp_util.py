from typing import Final

# digraphs not necessarily two characters.
# e.g., キ゚ャ is considered three.
DIGRAPHS: Final[list[str]] = ["りゃ", "みゃ", "ひゃ", "にゃ", "ちゃ", "しゃ", "きゃ", "りゅ", "みゅ", "ひゅ", "にゅ", "ちゅ", "しゅ", "きゅ", "りょ", "みょ", "ひょ", "にょ", "ちょ", "しょ", "きょ", "ぎゃ", "じゃ", "びゃ", "ぴゃ", "き゚ゃ", "ぎゅ", "じゅ", "びゅ", "ぴゅ", "き゚ゅ", "ぎょ", "じょ", "びょ", "ぴょ", "き゚ょ", "ヴぁ", "ふぁ", "ゔぃ", "うぃ", "ふぃ", "でぃ", "てぃ", "どぅ", "とぅ", "ゔぇ", "うぇ", "ふぇ", "ちぇ", "じぇ", "しぇ", "ゔぉ", "うぉ", "ふぉ", "リャ", "ミャ", "ヒャ", "ニャ", "チャ", "シャ", "キャ", "リュ", "ミュ", "ヒュ", "ニュ", "チュ", "シュ", "キュ", "リョ", "ミョ", "ヒョ", "ニョ", "チョ", "ショ", "キョ", "ギャ", "ジャ", "ビャ", "ピャ", "キ゚ャ", "ギュ", "ジュ", "ビュ", "ピュ", "キ゚ュ", "ギョ", "ジョ", "ビョ", "ピョ", "キ゚ョ", "ヴァ", "ファ", "ヴィ", "ウィ", "フィ", "ディ", "ティ", "ドゥ", "トゥ", "ヴェ", "ウェ", "フェ", "チェ", "ジェ", "シェ", "ヴォ", "ウォ", "フォ", "か゚", "き゚", "く゚", "け゚", "こ゚", "カ゚", "キ゚", "ク゚", "ケ゚", "コ゚"]


def split_into_mora(pronunciation):
    mora_list = []
    while len(pronunciation) > 0:
        found = False
        for d in DIGRAPHS:
            if pronunciation.find(d) == 0:
                pronunciation = pronunciation.removeprefix(d)
                mora_list.append(d)
                found = True
                break
        if not found:
            c = pronunciation[0]
            pronunciation = pronunciation.removeprefix(c)
            mora_list.append(c)
    return mora_list


KATAKANA_CHART = "ァアィイゥウェエォオカガカ゚キギキ゚クグク゚ケゲケ゚コゴコ゚サザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶヽヾ"
HIRAGANA_CHART = "ぁあぃいぅうぇえぉおかがか゚きぎき゚くぐく゚けげけ゚こごこ゚さざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖゝゞ"
KATA2HIRA = str.maketrans(KATAKANA_CHART, HIRAGANA_CHART)
HIRA2KATA = str.maketrans(HIRAGANA_CHART, KATAKANA_CHART)


def katakana_to_hiragana(kana):
    return kana.translate(KATA2HIRA)


def hiragana_to_katakana(kana):
    return kana.translate(HIRA2KATA)


def is_kana(word):
    for char in word:
        if char < "ぁ" or char > "ヾ":
            return False
    return True


def is_hiragana(word):
    for char in word:
        if char < "ぁ" or char > "ゞ":
            return False
    return True

