"""Build a printable phonics workbook (HTML -> PDF) from phonics_toc.xlsx.

Usage:
    python workbook/build_workbook.py            # writes workbook/phonics_workbook.html + .pdf

Each row of the TOC sheet becomes one A4 worksheet:
  1. 소리 내어 읽기 (target spelling highlighted)
  2. 따라 쓰기 (trace on 4-line guides)
  3. 빈칸 채우기 (target spelling blanked)
  4. 받아쓰기 (dictation lines; answers in the key at the back)
"""
import html
import os
import re
import subprocess
import sys

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "phonics_toc.xlsx")
OUT_HTML = os.path.join(HERE, "phonics_workbook.html")
OUT_PDF = os.path.join(HERE, "phonics_workbook.pdf")
CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")

SETS = {
    "Set 1": ("단모음 · 단자음", "#E4572E"),
    "Set 2": ("이중자 · 자음군", "#2E86AB"),
    "Set 3": ("장모음 · 모음팀", "#3BA55C"),
    "Set 4": ("r통제 · 이중모음 · 특수규칙", "#8E5BD0"),
    "Set 5": ("음절 · 어미 · 접사", "#E09F1F"),
}

# Per-page highlight rule. A regex with groups highlights only the groups;
# otherwise every whole match is highlighted.
RULES = {
    1: r"^[aeiou]",
    2: r"[tnm]",
    3: r"[spd]",
    4: r"[gcr]",
    5: r"[bhl]",
    6: r"[fkw]",
    7: r"[jvy]",
    8: r"qu|[zx]",
    9: r"sh|ch",
    10: r"th",
    11: r"tch",
    12: r"ck|ng",
    13: r"wh|ph",
    14: r"ss|ll|ff|zz",
    15: r"^(?:bl|cl|fl|gl|pl|sl|br|cr|dr|fr|gr|pr|tr|sc|sk|sm|sn|sp|st|sw)",
    16: r"(?:nd|nt|nk|mp|st|lt)$|^(?:spl|str|scr|spr|thr|shr|squ)",
    17: r"[aeiou]$",
    18: r"([aeiou])[^aeiou](e)$",
    19: r"ai|ay",
    20: r"ee|ea",
    21: r"oa|ow",
    22: r"igh|ie|y$",
    23: r"y$",
    24: r"oo|ew|ue|ui",
    25: r"oo",
    26: r"eigh",
    27: r"ar",
    28: r"ore|or",
    29: r"er|ir|ur",
    30: r"oi|oy",
    31: r"ou|ow",
    32: r"au|aw",
    33: r"[cg](?=[eiy])",
    34: r"kn|wr|mb|gn",
    36: r"le$",
    37: r"(?:es|ed|ing|s)$",
    38: r"(?:est|er|ly)$",
    39: r"^(?:un|re|dis)",
    40: r"^(?:mis|pre)",
    41: r"(?:ful|less|ness)$",
    42: r"(?:tion|sion|ture)$",
}

# Page 35 (schwa): the weak vowel can't be found by spelling, so mark it by index.
SCHWA = {
    "about": [0], "sofa": [3], "zebra": [4], "banana": [1, 5],
    "pencil": [4], "problem": [5], "animal": [4], "lemon": [3],
}


def spans(page, word):
    """Return [(start, end)] character spans to highlight in word."""
    if page == 35:
        return [(i, i + 1) for i in SCHWA.get(word, [])]
    rule = RULES.get(page)
    if not rule:
        return []
    out = []
    for m in re.finditer(rule, word):
        if m.re.groups:
            out += [m.span(g) for g in range(1, m.re.groups + 1) if m.group(g)]
        else:
            out.append(m.span())
    return out


def render(word, sp, mode):
    """mode 'hi' wraps spans in <b>, mode 'blank' replaces each letter with a box."""
    res, i = [], 0
    for s, e in sorted(sp):
        res.append(html.escape(word[i:s]))
        seg = word[s:e]
        if mode == "hi":
            res.append(f'<b class="hi">{html.escape(seg)}</b>')
        else:
            res.append('<span class="box"></span>' * len(seg))
        i = e
    res.append(html.escape(word[i:]))
    return "".join(res)


def parse_words(text):
    """Return [(word, tag)] from a TOC cell. Handles 'a: ant, apple · e: ...' and 'closed(cat)'."""
    words = []
    for chunk in re.split(r"\s*·\s*", str(text)):
        chunk = re.sub(r"^\s*\w\s*:\s*", "", chunk)
        for item in chunk.split(","):
            item = item.strip()
            if not item:
                continue
            m = re.match(r"([\w -]+?)\s*\((\w+)\)", item)
            w, tag = (m.group(2), m.group(1)) if m else (item, "")
            if w not in [x for x, _ in words]:
                words.append((w, tag))
    return words


def load_rows():
    ws = openpyxl.load_workbook(SRC, data_only=True).worksheets[0]
    rows = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[0] is None:
            continue
        page, set_, sound, rule, read, dict_ = r[:6]
        rows.append(dict(
            page=int(page), set=set_, sound=sound, rule=rule,
            read=parse_words(read), dict=[w for w, _ in parse_words(dict_)],
        ))
    return rows


CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #fff; }
body { font-variant-ligatures: none; font-family: 'Noto Sans KR', sans-serif; color: #1d2433; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.en { font-family: 'Andika', sans-serif; }
.page { width: 210mm; height: 297mm; padding: 11mm 13mm 9mm; position: relative; overflow: hidden; page-break-after: always; display: flex; flex-direction: column; }
.page:last-child { page-break-after: auto; }

/* header */
.hd { display: flex; align-items: stretch; gap: 4mm; margin-bottom: 4mm; }
.hd .tag { background: var(--c); color: #fff; border-radius: 4mm; padding: 2.5mm 4mm; display: flex; flex-direction: column; justify-content: center; align-items: center; min-width: 24mm; }
.hd .tag .set { font-size: 9pt; font-weight: 700; opacity: .9; }
.hd .tag .no { font-size: 24pt; font-weight: 900; line-height: 1; }
.hd .title { flex: 1; border: 0.6mm solid var(--c); border-radius: 4mm; padding: 2mm 5mm; display: flex; flex-direction: column; justify-content: center; }
.hd .sound { font-family: 'Andika', sans-serif; font-weight: 700; color: var(--c); line-height: 1.15; }
.hd .rule { font-size: 10pt; color: #4a5468; margin-top: 1mm; }
.hd .meta { width: 38mm; border: 0.3mm solid #c9d0dc; border-radius: 4mm; padding: 2mm 3mm; font-size: 8.5pt; color: #4a5468; display: flex; flex-direction: column; justify-content: space-around; }
.hd .meta .ln { border-bottom: 0.3mm solid #c9d0dc; padding-bottom: .5mm; }
.stars { font-size: 13pt; color: #d6dbe4; letter-spacing: 1mm; }

/* sections */
.sec { margin-bottom: 4.5mm; }
.sec h2 { font-size: 11pt; margin: 0 0 1.8mm; display: flex; align-items: center; gap: 2mm; }
.sec h2 .n { background: var(--c); color: #fff; width: 6mm; height: 6mm; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 9pt; }
.sec h2 small { font-weight: 400; color: #6b7487; font-size: 8.5pt; }
.hi { color: var(--c); font-weight: 700; }

.read { display: grid; grid-template-columns: repeat(4, 1fr); gap: 2mm; }
.read .w { border: 0.3mm solid #dfe3ea; border-radius: 2.5mm; padding: 1.6mm 1mm 1.2mm; text-align: center; background: #fafbfc; }
.read .w .t { font-size: 19pt; line-height: 1.15; }
.read .w .lab { font-size: 7pt; color: #8a93a6; font-family: 'Andika', sans-serif; }
.read .w .ck { font-size: 8pt; color: #b6bdca; letter-spacing: 1mm; }

.trace .row { position: relative; height: 15mm; margin-bottom: 3.2mm; }
.trace .row .g { position: absolute; left: 0; right: 0; }
.trace .row .g1 { top: 0; border-top: 0.25mm solid #9aa3b5; }
.trace .row .g2 { top: 5mm; border-top: 0.25mm dashed #c3c9d4; }
.trace .row .g3 { top: 10mm; border-top: 0.35mm solid #e06b6b; }
.trace .row .g4 { top: 15mm; border-top: 0.25mm solid #9aa3b5; }
.trace .row .word { position: absolute; left: 2mm; top: -2.3mm; font-family: 'Andika', sans-serif; font-size: 40pt; line-height: 1; color: #c4cbd8; letter-spacing: .6mm; }
.trace .row .sep { position: absolute; top: 0; bottom: 0; border-left: 0.3mm dotted #c9d0dc; }

.fill { display: grid; grid-template-columns: repeat(5, 1fr); gap: 2mm; }
.fill .f { border: 0.3mm solid #dfe3ea; border-radius: 2.5mm; padding: 2.5mm 1mm 2mm; text-align: center; }
.fill .f .t { font-size: 16pt; line-height: 1.2; white-space: nowrap; }
.fill .f .n { font-size: 7.5pt; color: #8a93a6; }
.box { display: inline-block; width: 4.6mm; height: 6.2mm; border: 0.35mm solid var(--c); border-radius: 1mm; margin: 0 .25mm; vertical-align: -1mm; background: #fff; }
.bank { font-size: 9pt; color: #4a5468; margin: -0.5mm 0 1.8mm; }
.bank span { font-family: 'Andika', sans-serif; font-size: 11pt; color: var(--c); font-weight: 700; }

.dict { display: grid; grid-template-columns: 1fr 1fr; gap: 0 8mm; }
.dict .d { display: flex; align-items: flex-end; gap: 2mm; height: 12mm; border-bottom: 0.3mm solid #9aa3b5; font-size: 9pt; color: #8a93a6; padding-bottom: .8mm; }

.ft { margin-top: auto; display: flex; justify-content: space-between; align-items: center; font-size: 8pt; color: #8a93a6; border-top: 0.3mm solid #e3e7ee; padding-top: 2mm; }
.ft .sign { border: 0.3mm solid #c9d0dc; border-radius: 2mm; padding: 1mm 3mm; }

/* cover / toc / key */
.cover { justify-content: center; align-items: center; text-align: center; }
.cover h1 { font-family: 'Andika', sans-serif; font-size: 48pt; margin: 0; color: #1d2433; }
.cover .sub { font-size: 14pt; color: #4a5468; margin: 3mm 0 10mm; }
.cover .letters { font-family: 'Andika', sans-serif; font-size: 30pt; font-weight: 700; letter-spacing: 3mm; margin-bottom: 12mm; }
.cover .name { font-size: 13pt; border-bottom: 0.4mm solid #1d2433; width: 110mm; margin: 0 auto 4mm; text-align: left; padding: 2mm; }
.cover .tracker { margin-top: 12mm; width: 170mm; text-align: left; }
.cover .tracker h3 { font-size: 11pt; margin: 0 0 2mm; }
.cover .tracker .rowset { display: flex; align-items: center; gap: 2mm; margin-bottom: 2mm; font-size: 9pt; }
.cover .tracker .rowset .lbl { width: 14mm; font-weight: 700; }
.cover .tracker .dot { width: 9mm; height: 9mm; border-radius: 50%; border: 0.4mm solid; display: inline-flex; align-items: center; justify-content: center; font-size: 8pt; color: #8a93a6; }
.how { margin-top: 10mm; width: 170mm; text-align: left; font-size: 9.5pt; color: #4a5468; border: 0.3mm solid #dfe3ea; border-radius: 3mm; padding: 3mm 5mm; }
.how ol { margin: 1mm 0 0; padding-left: 5mm; }

h1.pt { font-size: 18pt; margin: 0 0 4mm; }
table.toc { width: 100%; border-collapse: collapse; font-size: 8.4pt; }
table.toc th { background: #1d2433; color: #fff; padding: 1.4mm 2mm; text-align: left; }
table.toc td { padding: 1.05mm 2mm; border-bottom: 0.25mm solid #e3e7ee; vertical-align: top; }
table.toc td.snd { font-family: 'Andika', sans-serif; font-weight: 700; }
table.toc .chip { display: inline-block; color: #fff; border-radius: 1.5mm; padding: 0 1.5mm; font-size: 7.5pt; font-weight: 700; }
table.key td.ans { font-family: 'Andika', sans-serif; font-size: 10pt; }
"""


def sound_size(text):
    n = len(text)
    return "30pt" if n <= 14 else "22pt" if n <= 26 else "15pt" if n <= 50 else "12pt"


def worksheet(r):
    color = SETS.get(r["set"], ("", "#444"))[1]
    p = r["page"]
    read_cells = []
    for w, tag in r["read"]:
        lab = f'<div class="lab">{html.escape(tag)}</div>' if tag else ""
        read_cells.append(
            f'<div class="w"><div class="t en">{render(w, spans(p, w), "hi")}</div>{lab}'
            f'<div class="ck">○○○</div></div>')

    trace_rows = []
    for w in r["dict"][:5]:
        width = max(46, len(w) * 8.6 + 12)
        trace_rows.append(
            f'<div class="row"><div class="g g1"></div><div class="g g2"></div><div class="g g3"></div>'
            f'<div class="g g4"></div><div class="word">{html.escape(w)}</div>'
            f'<div class="sep" style="left:{width:.0f}mm"></div></div>')

    fill_cells = []
    for i, w in enumerate(r["dict"][:5], 1):
        sp = spans(p, w)
        t = render(w, sp, "blank") if sp else html.escape(w)
        fill_cells.append(f'<div class="f"><div class="t en">{t}</div><div class="n">{i}</div></div>')

    dict_lines = "".join(f'<div class="d">{i}.</div>' for i in range(1, 7))

    return f"""
<section class="page" style="--c:{color}">
  <div class="hd">
    <div class="tag"><div class="set">{html.escape(r['set'])}</div><div class="no">{p}</div></div>
    <div class="title"><div class="sound" style="font-size:{sound_size(r['sound'])}">{html.escape(r['sound'])}</div>
      <div class="rule">{html.escape(r['rule'])}</div></div>
    <div class="meta"><div class="ln">날짜&nbsp;&nbsp;&nbsp;&nbsp;/</div><div>오늘의 별</div><div class="stars">★★★</div></div>
  </div>

  <div class="sec"><h2><span class="n">1</span>소리 내어 읽기 <small>색깔 글자의 소리에 집중! 한 번 읽을 때마다 ○ 하나씩 칠해요.</small></h2>
    <div class="read">{''.join(read_cells)}</div></div>

  <div class="sec trace"><h2><span class="n">2</span>따라 쓰기 <small>회색 글자를 따라 쓰고, 점선 오른쪽에 두 번 더 써요.</small></h2>
    {''.join(trace_rows)}</div>

  <div class="sec"><h2><span class="n">3</span>빈칸 채우기 <small>네모 칸에 들어갈 글자를 써요.</small></h2>
    <div class="bank">힌트 소리: <span>{html.escape(r['sound'])}</span></div>
    <div class="fill">{''.join(fill_cells)}</div></div>

  <div class="sec"><h2><span class="n">4</span>받아쓰기 <small>불러 주는 단어를 듣고 써요. (정답은 맨 뒤)</small></h2>
    <div class="dict">{dict_lines}</div></div>

  <div class="ft"><span>Phonics Workbook · {html.escape(r['set'])} {html.escape(SETS.get(r['set'], ('',))[0])}</span>
    <span class="sign">확인 ________</span><span>{p} / 42</span></div>
</section>"""


def cover(rows):
    tracker = []
    for s, (name, col) in SETS.items():
        dots = "".join(
            f'<span class="dot" style="border-color:{col}">{r["page"]}</span>'
            for r in rows if r["set"] == s)
        tracker.append(f'<div class="rowset"><span class="lbl" style="color:{col}">{s}</span>{dots}</div>')
    return f"""
<section class="page cover">
  <h1>Phonics Workbook</h1>
  <div class="sub">파닉스 워크북 · 5 Sets · 42 Pages · {sum(len(r['read']) for r in rows)} Words</div>
  <div class="letters"><span style="color:#E4572E">a</span> <span style="color:#2E86AB">sh</span> <span style="color:#3BA55C">ee</span> <span style="color:#8E5BD0">ar</span> <span style="color:#E09F1F">-tion</span></div>
  <div class="name">이름 :</div>
  <div class="name">시작한 날 :</div>
  <div class="tracker"><h3>진도표 — 끝낸 페이지에 색칠하거나 스티커를 붙여요</h3>{''.join(tracker)}</div>
  <div class="how"><b>하루 한 장 사용법</b><ol>
    <li><b>읽기</b> — 색깔 글자 소리를 크게 말하며 단어를 3번 읽어요.</li>
    <li><b>따라 쓰기</b> — 회색 글자를 따라 쓰고 두 번 더 써요. 빨간 선이 글자가 앉는 줄이에요.</li>
    <li><b>빈칸 채우기</b> — 오늘 배운 소리 글자로 네모를 채워요.</li>
    <li><b>받아쓰기</b> — 어른이 맨 뒤 정답표의 단어를 불러 주면 들리는 대로 써요.</li></ol></div>
</section>"""


def toc(rows):
    trs = []
    for r in rows:
        col = SETS[r["set"]][1]
        trs.append(
            f'<tr><td>{r["page"]}</td><td><span class="chip" style="background:{col}">{r["set"]}</span></td>'
            f'<td class="snd" style="color:{col}">{html.escape(r["sound"])}</td><td>{html.escape(r["rule"])}</td></tr>')
    return f"""
<section class="page"><h1 class="pt">목차</h1>
<table class="toc"><tr><th>쪽</th><th>세트</th><th>소리</th><th>묶음 기준</th></tr>{''.join(trs)}</table></section>"""


def key(rows):
    pages = []
    for half in (rows[:21], rows[21:]):
        trs = "".join(
            f'<tr><td>{r["page"]}</td><td class="snd" style="color:{SETS[r["set"]][1]}">{html.escape(r["sound"])}</td>'
            f'<td class="ans">{html.escape(", ".join(r["dict"]))}</td></tr>' for r in half)
        pages.append(f"""
<section class="page"><h1 class="pt">정답 · 받아쓰기 단어 ({half[0]['page']}–{half[-1]['page']}쪽)</h1>
<p style="font-size:9pt;color:#6b7487;margin:-2mm 0 3mm">3번 빈칸 채우기와 4번 받아쓰기의 정답입니다. 받아쓰기는 순서를 섞어 불러 줘도 좋아요.</p>
<table class="toc key"><tr><th>쪽</th><th>소리</th><th>단어</th></tr>{trs}</table></section>""")
    return "".join(pages)


def build():
    rows = load_rows()
    body = cover(rows) + toc(rows) + "".join(worksheet(r) for r in rows) + key(rows)
    doc = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>Phonics Workbook</title>
<link href="https://fonts.googleapis.com/css2?family=Andika:wght@400;700&family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>{body}</body></html>"""
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(doc)
    subprocess.run([
        CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
        "--virtual-time-budget=15000", f"--print-to-pdf={OUT_PDF}", "file://" + OUT_HTML,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("wrote", OUT_HTML, OUT_PDF, file=sys.stderr)


if __name__ == "__main__":
    build()
