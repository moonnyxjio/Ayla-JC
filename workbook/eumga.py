"""English phonics -> 한글 음가 (per grapheme) and 합쳐 읽기 (composed Hangul).

    >>> eumga(2, "cat")
    [('c', 'ㅋ'), ('a', 'ㅐ'), ('t', 'ㅌ')]
    >>> reading(2, "cat")
    '캣'

Conventions (Korean phonics-academy style, American English):
  short vowels a=ㅐ e=ㅔ i=ㅣ o=ㅏ u=ㅓ · long vowels say their name (a=에이, i=아이, o=오우, u=유, e=이)
  r-controlled vowels keep a small r (car = 카r) · silent letters are shown as ×
  In 합쳐 읽기 a final t/k/p after a short vowel becomes 받침 ㅅ/ㄱ/ㅂ (cat 캣, duck 덕, cup 컵);
  n/m/l/ng can always be 받침; any other leftover consonant takes ㅡ (dog 다그, bus 버스).
"""
import re

INI = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
VOW = "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"
COD = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ",
       "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]

SHORT = {"a": "ㅐ", "e": "ㅔ", "i": "ㅣ", "o": "ㅏ", "u": "ㅓ"}
LONG = {"a": "ㅔㅣ", "e": "ㅣ", "i": "ㅏㅣ", "o": "ㅗㅜ", "u": "ㅠ"}
CONS = {"b": "ㅂ", "d": "ㄷ", "f": "ㅍ", "g": "ㄱ", "h": "ㅎ", "j": "ㅈ", "k": "ㅋ", "l": "ㄹ", "m": "ㅁ",
        "n": "ㄴ", "p": "ㅍ", "r": "ㄹ", "s": "ㅅ", "t": "ㅌ", "v": "ㅂ", "z": "ㅈ"}
STOP_CODA = {"ㅋ": "ㄱ", "ㅍ": "ㅂ", "ㅌ": "ㅅ"}
SONOR_CODA = {"ㄴ", "ㄹ", "ㅁ", "ㅇ"}
GLIDE = {("W", "ㅏ"): "ㅘ", ("W", "ㅐ"): "ㅙ", ("W", "ㅔ"): "ㅞ", ("W", "ㅣ"): "ㅟ", ("W", "ㅓ"): "ㅝ",
         ("W", "ㅗ"): "ㅝ", ("W", "ㅜ"): "ㅜ", ("W", "ㅠ"): "ㅠ",
         ("Y", "ㅏ"): "ㅑ", ("Y", "ㅐ"): "ㅒ", ("Y", "ㅔ"): "ㅖ", ("Y", "ㅓ"): "ㅕ", ("Y", "ㅗ"): "ㅛ",
         ("Y", "ㅜ"): "ㅠ", ("Y", "ㅣ"): "ㅣ", ("Y", "ㅠ"): "ㅠ"}
# sh / ch + vowel -> (initial, vowel)
SPECIAL = {
    "SH": ("ㅅ", {"ㅏ": "ㅑ", "ㅐ": "ㅒ", "ㅔ": "ㅖ", "ㅓ": "ㅕ", "ㅗ": "ㅛ", "ㅜ": "ㅠ", "ㅣ": "ㅟ", "ㅠ": "ㅠ", None: "ㅟ"}),
    "CH": ("ㅊ", {"ㅏ": "ㅏ", "ㅐ": "ㅐ", "ㅔ": "ㅔ", "ㅓ": "ㅓ", "ㅗ": "ㅗ", "ㅜ": "ㅜ", "ㅣ": "ㅣ", "ㅠ": "ㅜ", None: "ㅣ"}),
}
STOP_SRC = {"k", "c", "t", "p", "x", "tt", "pp"}
VOICED_TH = {"than", "that", "them", "then", "this", "thus", "the", "there", "they"}
SOFT_G = {"gem", "gym", "cage", "page", "giant", "giraffe", "gentle", "huge", "large", "orange", "bridge"}
SCHWA = {"about": [0], "sofa": [3], "zebra": [4], "banana": [1, 5], "pencil": [4], "problem": [5],
         "animal": [2, 4], "lemon": [3]}

# Whole-word readings where the rules give an unnatural result (the boxes still follow the rules).
READING_OVERRIDE = {
    "good": "굿", "cage": "케이지", "page": "페이지", "helpless": "헬프레스", "mislead": "미스리드",
    "misread": "미스리드", "misplace": "미스플레이스", "misprint": "미스프린트", "mistrust": "미스트러스트",
    "dislike": "디스라이크", "jumped": "점프트", "careless": "케어레스",
}

# Irregular words: (boxes, reading) written by hand so the two always agree.
CELL_OVERRIDE = {
    "photo": ([("ph", "ㅍ"), ("o", "오우"), ("t", "ㅌ"), ("o", "오우")], "포우토우"),
    "baby": ([("b", "ㅂ"), ("a", "에이"), ("b", "ㅂ"), ("y", "ㅣ")], "베이비"),
    "preview": ([("p", "ㅍ"), ("r", "ㄹ"), ("e", "ㅣ"), ("v", "ㅂ"), ("iew", "ㅠ")], "프리뷰"),
    "preschool": ([("p", "ㅍ"), ("r", "ㄹ"), ("e", "ㅣ"), ("s", "ㅅ"), ("ch", "ㅋ"), ("oo", "ㅜ"), ("l", "ㄹ")], "프리스쿨"),
    "useful": ([("u", "유"), ("s", "ㅅ"), ("e", "×"), ("ful", "풀")], "유스풀"),
    "hopeful": ([("h", "ㅎ"), ("o", "오우"), ("p", "ㅍ"), ("e", "×"), ("ful", "풀")], "호우프풀"),
    "careful": ([("c", "ㅋ"), ("are", "에어r"), ("ful", "풀")], "케어풀"),
    "redo": ([("r", "ㄹ"), ("e", "ㅣ"), ("d", "ㄷ"), ("o", "ㅜ")], "리두"),
    "undo": ([("u", "ㅓ"), ("n", "ㄴ"), ("d", "ㄷ"), ("o", "ㅜ")], "언두"),
    "misuse": ([("m", "ㅁ"), ("i", "ㅣ"), ("s", "ㅅ"), ("u", "유"), ("s", "ㅈ"), ("e", "×")], "미스유즈"),
    "comb": ([("c", "ㅋ"), ("o", "오우"), ("mb", "ㅁ")], "코움"),
    "watch": ([("w", "ㅜ"), ("a", "ㅏ"), ("tch", "치")], "와치"),
    "about": ([("a", "ㅓ"), ("b", "ㅂ"), ("ou", "아우"), ("t", "ㅌ")], "어바웃"),
    "sofa": ([("s", "ㅅ"), ("o", "오우"), ("f", "ㅍ"), ("a", "ㅓ")], "소우퍼"),
    "zebra": ([("z", "ㅈ"), ("e", "ㅣ"), ("b", "ㅂ"), ("r", "ㄹ"), ("a", "ㅓ")], "지브러"),
    "disagree": ([("d", "ㄷ"), ("i", "ㅣ"), ("s", "ㅅ"), ("a", "ㅓ"), ("g", "ㄱ"), ("r", "ㄹ"), ("ee", "ㅣ")], "디스어그리"),
    "music": ([("m", "ㅁ"), ("u", "유"), ("s", "ㅈ"), ("i", "ㅣ"), ("c", "ㅋ")], "뮤직"),
    "full": ([("f", "ㅍ"), ("u", "ㅜ"), ("ll", "ㄹ")], "풀"),
    "umbrella": ([("u", "ㅓ"), ("m", "ㅁ"), ("b", "ㅂ"), ("r", "ㄹ"), ("e", "ㅔ"), ("ll", "ㄹ"), ("a", "ㅓ")], "엄브렐러"),
    "question": ([("qu", "ㅋㅜ"), ("e", "ㅔ"), ("s", "ㅅ"), ("tion", "천")], "퀘스천"),
    "yak": ([("y", "ㅣ"), ("a", "ㅐ"), ("k", "ㅋ")], "얘크"),
    "eighty": ([("eigh", "에이"), ("t", "ㅌ"), ("y", "ㅣ")], "에이티"),
    "otter": ([("o", "ㅏ"), ("tt", "ㅌ"), ("er", "ㅓr")], "아터"),
}


def tokenize(page, word):
    """Return [(grapheme, tokens)] where tokens are ('C', jamo) ('V', jamo, long) ('G', W|Y)
    ('S', SH|CH) ('R',) or [] for a silent letter."""
    w = word.lower()
    out, i, n = [], 0, len(w)
    magic = re.search(r"([aeiou])([^aeiouwxy]|th|ch|sh)e$", w)
    magic_v = magic.start(1) if magic and len(w) >= 3 and not w.endswith("le") else -1

    def nxt(k):
        return w[k] if k < n else "#"

    while i < n:
        rest = w[i:]
        # suffixes / multi-letter units
        if re.match(r"ssion$", rest):
            out.append((rest, [("S", "SH"), ("V", "ㅓ", False), ("C", "ㄴ")])); break
        if page >= 42 and re.match(r"(tion|sion)$", rest):
            out.append((rest, [("S", "SH"), ("V", "ㅓ", False), ("C", "ㄴ")])); break
        if re.match(r"ful$", rest) and i > 0:
            out.append((rest, [("C", "ㅍ", "f"), ("V", "ㅜ", False), ("C", "ㄹ")])); break
        if re.match(r"ture$", rest):
            out.append((rest, [("S", "CH"), ("V", "ㅓ", False), ("R",)])); break
        if re.match(r"le$", rest) and i > 0 and w[i - 1] not in "aeiou":
            out.append(("le", [("V", "ㅡ", False), ("C", "ㄹ")])); break
        if page == 37 and re.match(r"ed$", rest):
            prev = w[i - 1]
            toks = [("V", "ㅣ", False), ("C", "ㄷ")] if prev in "td" else \
                [("C", "ㅌ")] if prev in "pkcsxhf" else [("C", "ㄷ")]
            out.append(("ed", toks)); break
        if page == 37 and re.match(r"es$", rest) and w[i - 1] in "sxhz":
            out.append(("es", [("V", "ㅣ", False), ("C", "ㅈ")])); break
        m = re.match(r"all|eigh|tch|igh|ore|are|air|ear|eer", rest)
        if m:
            g = m.group(0)
            toks = {"all": [("V", "ㅗ", False), ("C", "ㄹ", "l")], "eigh": [("V", "ㅔ", True), ("V", "ㅣ", True)],
                    "tch": [("S", "CH")], "igh": [("V", "ㅏ", True), ("V", "ㅣ", True)],
                    "ore": [("V", "ㅗ", True), ("R",)], "are": [("V", "ㅔ", True), ("V", "ㅓ", True), ("R",)],
                    "air": [("V", "ㅔ", True), ("V", "ㅓ", True), ("R",)],
                    "ear": [("V", "ㅣ", True), ("V", "ㅓ", True), ("R",)],
                    "eer": [("V", "ㅣ", True), ("V", "ㅓ", True), ("R",)]}[g]
            out.append((g, toks)); i += len(g); continue
        two = rest[:2]
        if two in ("sh", "ch"):
            out.append((two, [("S", two.upper())])); i += 2; continue
        if two == "th":
            out.append((two, [("C", "ㄷ" if w in VOICED_TH else "ㅆ")])); i += 2; continue
        if two in ("ck",):
            out.append((two, [("C", "ㅋ", "k")])); i += 2; continue
        if two == "ng":
            out.append((two, [("C", "ㅇ")])); i += 2; continue
        if two in ("wh",):
            out.append((two, [("G", "W")])); i += 2; continue
        if two == "ph":
            out.append((two, [("C", "ㅍ")])); i += 2; continue
        if two == "qu":
            out.append((two, [("C", "ㅋ", "qu"), ("G", "W")])); i += 2; continue
        if two in ("kn", "gn") and i == 0:
            out.append((two, [("C", "ㄴ")])); i += 2; continue
        if two == "wr" and i == 0:
            out.append((two, [("C", "ㄹ")])); i += 2; continue
        if two == "mb" and i + 2 == n:
            out.append((two, [("C", "ㅁ")])); i += 2; continue
        if two == "gn" and i + 2 == n:
            out.append((two, [("C", "ㄴ")])); i += 2; continue
        if two in ("ai", "ay"):
            out.append((two, [("V", "ㅔ", True), ("V", "ㅣ", True)])); i += 2; continue
        if two in ("ee", "ea"):
            out.append((two, [("V", "ㅣ", True)])); i += 2; continue
        if two == "oa":
            out.append((two, [("V", "ㅗ", True), ("V", "ㅜ", True)])); i += 2; continue
        if two == "ow":
            long_o = page == 21 or w in ("snow", "grow", "slow", "bowl", "know", "slowly")
            out.append((two, [("V", "ㅗ", True), ("V", "ㅜ", True)] if long_o else
                        [("V", "ㅏ", True), ("V", "ㅜ", True)])); i += 2; continue
        if two == "ou":
            out.append((two, [("V", "ㅏ", True), ("V", "ㅜ", True)])); i += 2; continue
        if two == "ie":
            out.append((two, [("V", "ㅏ", True), ("V", "ㅣ", True)])); i += 2; continue
        if two == "oo":
            out.append((two, [("V", "ㅜ", page != 25)])); i += 2; continue
        if two in ("ew", "ue", "ui"):
            prev = w[max(0, i - 2):i]
            v = "ㅜ" if (prev[-1:] in ("r", "l", "j") or prev == "ch" or prev.endswith("s")) else "ㅠ"
            out.append((two, [("V", v, True)])); i += 2; continue
        if two in ("oi", "oy"):
            out.append((two, [("V", "ㅗ", True), ("V", "ㅣ", True)])); i += 2; continue
        if two in ("au", "aw"):
            out.append((two, [("V", "ㅗ", True)])); i += 2; continue
        if two in ("ar",) and nxt(i + 2) not in "aeiouy":
            out.append((two, [("V", "ㅏ", True), ("R",)])); i += 2; continue
        if two == "or" and nxt(i + 2) not in "aeiouy":
            out.append((two, [("V", "ㅗ", True), ("R",)])); i += 2; continue
        if two in ("er", "ir", "ur") and nxt(i + 2) not in "aeiouy":
            out.append((two, [("V", "ㅓ", True), ("R",)])); i += 2; continue
        if len(two) == 2 and two[0] == two[1] and two[0] in "bdfglmnprstz":
            out.append((two, [("C", CONS[two[0]], two)])); i += 2; continue
        c = w[i]
        if c in "aeiou":
            if i == n - 1 and c == "e" and n >= 3:
                out.append((c, [])); i += 1; continue          # silent final e
            if page == 35 and i in SCHWA.get(w, []):
                out.append((c, [("V", "ㅓ", False)])); i += 1; continue
            tail = w[i + 1:]
            open_syl = tail in ("tion", "sion", "ture") or bool(re.fullmatch(r"[bcdfgkpstvz]le", tail))
            is_long = i == magic_v or (i == n - 1 and n <= 3) or (page == 17 and i == n - 1) or open_syl
            if c == "i" and re.match(r"[nl]d", tail):
                is_long = True                                   # kind, mind, wild
            if c == "e" and i in (1, 2) and re.match(r"(pre|re)", w) and page in (39, 40) and i == w.index("e"):
                is_long = True                                   # re-, pre-
            if c == "o" and w in ("go", "no", "so"):
                is_long = True
            out.append((c, [("V", ch, True) for ch in LONG[c]] if is_long else [("V", SHORT[c], False)]))
            i += 1; continue
        if c == "y":
            if i == 0:
                out.append((c, [("G", "Y")]))
            elif i == n - 1 and len([x for x in w if x in "aeiou"]) == 0:
                out.append((c, [("V", "ㅏ", True), ("V", "ㅣ", True)]))   # my, fly
            else:
                out.append((c, [("V", "ㅣ", False)]))                    # happy, gym
            i += 1; continue
        if c == "w":
            out.append((c, [("G", "W")])); i += 1; continue
        if c == "x":
            out.append((c, [("C", "ㅋ", "x"), ("C", "ㅅ", "s")])); i += 1; continue
        if c == "c":
            out.append((c, [("C", "ㅅ", "s") if nxt(i + 1) in ("e", "i", "y") else ("C", "ㅋ", "k")])); i += 1; continue
        if c == "g":
            soft = (w in SOFT_G or page == 33) and nxt(i + 1) in ("e", "i", "y")
            out.append((c, [("C", "ㅈ" if soft else "ㄱ")])); i += 1; continue
        if c == "h" and i > 0 and w[i - 1] == "g":
            out.append((c, [])); i += 1; continue
        out.append((c, [("C", CONS.get(c, c), c)])); i += 1
    return out


def display(tokens):
    """How one grapheme's 음가 is written in its box."""
    if not tokens:
        return "×"
    s = ""
    for t in tokens:
        if t[0] == "C":
            s += t[1]
        elif t[0] == "V":
            s += t[1]
        elif t[0] == "G":
            s += "ㅜ" if t[1] == "W" else "ㅣ"
        elif t[0] == "S":
            s += "쉬" if t[1] == "SH" else "치"
        elif t[0] == "R":
            s += "r"
    # long vowel pairs read better as syllables (에이, 아이, 오우, 아우, 오이)
    for a, b in (("ㅔㅣ", "에이"), ("ㅏㅣ", "아이"), ("ㅗㅜ", "오우"), ("ㅏㅜ", "아우"), ("ㅗㅣ", "오이"),
                 ("ㅔㅓ", "에어"), ("ㅣㅓ", "이어")):
        s = s.replace(a, b)
    return s


UNIT_DISPLAY = {"tion": "션", "sion": "션", "ssion": "션", "ture": "처r", "le": "을", "ful": "풀"}


def eumga(page, word):
    if word.lower() in CELL_OVERRIDE:
        return CELL_OVERRIDE[word.lower()][0]
    return [(g, UNIT_DISPLAY.get(g) if g in UNIT_DISPLAY and t else display(t)) for g, t in tokenize(page, word)]


def _compose(ini, vow, cod=""):
    return chr(0xAC00 + (INI.index(ini) * 21 + VOW.index(vow)) * 28 + COD.index(cod))


def reading(page, word):
    if word.lower() in READING_OVERRIDE:
        return READING_OVERRIDE[word.lower()]
    if word.lower() in CELL_OVERRIDE:
        return CELL_OVERRIDE[word.lower()][1]
    toks = [t for _, ts in tokenize(page, word) for t in ts]
    syl = []                      # [ini, vow, coda, long, extra, cluster]
    pend, glide = None, None

    def add(ini, vow, long_=False, cluster=False):
        syl.append([ini, vow, "", long_, "", cluster])

    def flush():
        nonlocal pend
        if pend is None:
            return
        if pend in SPECIAL:
            ini, vm = SPECIAL[pend]
            add(ini, vm[None], cluster=True)
        else:
            add(pend, "ㅡ", cluster=True)
        pend = None

    def peek(k):
        for t in toks[k + 1:]:
            if t[0] != "R":
                return t
        return None

    for k, t in enumerate(toks):
        kind = t[0]
        if kind == "C":
            j, src = t[1], (t[2] if len(t) > 2 else "")
            nt = peek(k)
            nk = nt[0] if nt else None
            if nk == "V" or (nk == "G" and nt[1] == "W" and (j == "ㅋ" and src == "qu")) or (nk == "G" and nt[1] == "Y"):
                flush()
                pend = j
                if j == "ㄹ" and src in ("l", "ll") and syl and not syl[-1][2]:
                    syl[-1][2] = "ㄹ"            # bl -> 블ㄹ, and intervocalic l: taller 톨러
                continue
            if pend is None and syl and not syl[-1][2] and not syl[-1][5]:
                last = syl[-1]
                if j in SONOR_CODA:
                    after = peek(k + 1) if nt else None
                    ng = j == "ㄴ" and nt and nt[0] == "C" and nt[1] in ("ㅋ", "ㄱ") and (after is None or after[0] == "C")
                    last[2] = "ㅇ" if ng else j
                    continue
                stop_ok = j in STOP_CODA and src in STOP_SRC and not last[3] and (
                    nk is None or src == "x" or nk == "S" or (nt[0] == "C" and nt[1] in ("ㅌ", "ㅅ"))
                    or (src == "k" and nt[0] == "C" and nt[1] == "ㄹ"))
                if stop_ok:
                    last[2] = STOP_CODA[j]
                    continue
            flush()
            pend = j
            flush()
        elif kind == "S":
            flush()
            if peek(k) and peek(k)[0] == "V":
                pend = t[1]
            else:
                pend = t[1]
                flush()
                syl[-1][5] = False          # 쉬/치 can take no coda anyway; treat as full syllable
        elif kind == "G":
            if pend is None:
                pend = "ㅇ"
            elif pend not in ("ㅋ",) and t[1] == "W":
                flush()
                pend = "ㅇ"
            glide = t[1]
        elif kind == "V":
            v = t[1]
            if glide:
                v = GLIDE.get((glide, v), v)
                glide = None
            if pend in SPECIAL:
                ini, vm = SPECIAL[pend]
                add(ini, vm.get(v, v), t[2])
            else:
                add(pend or "ㅇ", v, t[2])
            pend = None
        elif kind == "R":
            pass                              # r-controlled: the r shows in the 음가 box, not in 합쳐 읽기
    flush()
    return "".join(_compose(ini, vow, cod) + extra for ini, vow, cod, _, extra, _ in syl)


def syllables(page, word):
    """Rough English syllable split for the 끊어 읽기 answer (VC|CV, V|CV, double letters, C+le)."""
    gs = tokenize(page, word)
    is_v = [any(t[0] == "V" for t in ts) for _, ts in gs]
    if sum(is_v) <= 1:
        return [word]
    pos, p = [], 0
    for g, _ in gs:
        pos.append(p)
        p += len(g)
    vidx = [i for i, v in enumerate(is_v) if v]
    cuts = []
    for a, b in zip(vidx, vidx[1:]):
        between = b - a - 1
        if between <= 0:
            cuts.append(pos[b])
        elif between == 1:
            g = gs[a + 1][0]
            if len(g) == 2 and g[0] == g[1]:
                cuts.append(pos[a + 1] + 1)                   # rab|bit
            elif gs[b][0] == "le":
                cuts.append(pos[a + 1])                       # ta|ble
            else:
                long_ = any(t[0] == "V" and t[2] for t in gs[a][1])
                cuts.append(pos[a + 1] if long_ else pos[b])  # ho|tel vs lem|on
        elif gs[b][0] == "le":
            cuts.append(pos[b - 1])
        else:
            pair = gs[b - 2][0] + gs[b - 1][0]
            blend = re.fullmatch(r"[bcfgp][lr]|[dt]r|s[cklmnpqtw]|thr|shr|str|spr|spl|scr", pair)
            cuts.append(pos[b - 2] if blend else pos[b - 1])
    parts, last = [], 0
    for c in cuts:
        parts.append(word[last:c])
        last = c
    parts.append(word[last:])
    return [x for x in parts if x]
