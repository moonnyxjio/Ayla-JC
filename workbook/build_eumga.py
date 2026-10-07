"""Build the 음가 쓰기 (phonics → 한글 음가) workbook in the academy test style.

Usage:
    python workbook/build_eumga.py     # writes workbook/phonics_eumga_workbook.html + .pdf

Per lesson (one page): 소리표 → 예시 → A 음가 쓰기 10문항 (/10) → B 음가 보고 영어로 쓰기 4문항.
After each Set: Phonics Test (10 words, Name/Class/Score). Answer key at the back.
"""
import html
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_workbook as WB  # noqa: E402
from eumga import eumga, reading, syllables, tokenize  # noqa: E402

OUT_HTML = os.path.join(HERE, "phonics_eumga_workbook.html")
OUT_PDF = os.path.join(HERE, "phonics_eumga_workbook.pdf")
CSS_FILE = os.path.join(HERE, "eumga.css")


def target_flags(page, word):
    """For each grapheme of word: does it overlap today's highlighted spelling?"""
    sp = WB.spans(page, word)
    flags, p = [], 0
    for g, _ in tokenize(page, word):
        flags.append(any(s < p + len(g) and p < e for s, e in sp))
        p += len(g)
    return flags


def chart(page, words):
    seen = {}
    for w in words:
        for (g, ja), hit in zip(eumga(page, w), target_flags(page, w)):
            if hit and g not in seen and ja != "×":
                seen[g] = ja
    if page == 18:
        seen["끝 e"] = "×"
    if page == 34:
        seen = {"kn": "ㄴ (k ×)", "wr": "ㄹ (w ×)", "mb": "ㅁ (b ×)", "gn": "ㄴ (g ×)"}
    return list(seen.items())[:9]


def word_cells(page, word, filled=False, hl=True):
    cells = []
    for (g, ja), hit in zip(eumga(page, word), target_flags(page, word)):
        cls = "gc hit" if (hit and hl) else "gc"
        box = f'<div class="jb fill">{html.escape(ja)}</div>' if filled else '<div class="jb"></div>'
        cells.append(f'<div class="{cls}"><div class="gl en">{html.escape(g)}</div>{box}</div>')
    return "".join(cells)


def item(page, n, word, filled=False):
    multi = len(syllables(page, word)) > 1
    hint = '<span class="cut">✂ 음절 선 긋기</span>' if multi and not filled else ""
    ans = f'<span class="ans">{html.escape(reading(page, word))}</span>' if filled else ""
    return f"""
    <div class="it{' ex' if filled else ''}">
      <div class="num">{n}</div>
      <div class="body"><div class="cells">{word_cells(page, word, filled)}</div>
        <div class="rd">→ <span class="ln">{ans}</span>{hint}</div></div>
    </div>"""


def reverse_item(page, n, word):
    boxes = "".join(f'<div class="rj">{html.escape(ja)}</div>' for _, ja in eumga(page, word))
    w = word.lower()
    hint = (WB.EMOJI.get(w, "") + " " + WB.GLOSS.get(w, "")).strip()
    hint = f'<div class="hint">{html.escape(hint)}</div>' if hint else ""
    return f"""
    <div class="rv"><div class="num">{n}</div><div class="rjs">{boxes}</div>{hint}<div class="arrow">→</div><div class="wl"></div></div>"""


def head(title, sub, color, score=10):
    return f"""
  <div class="th" style="--c:{color}">
    <div class="tt"><b>{title}</b></div>
    <div class="ts">{sub}</div>
  </div>
  <table class="who"><tr><td>E. Name :</td><td>K. Name :</td></tr>
    <tr><td>Class :</td><td>Score : <span class="sc"></span> / {score}</td></tr></table>"""


def pick_words(r):
    words = list(dict.fromkeys(r["dict"] + [w for w, _ in r["read"]]))
    if r["page"] in WB.SORT:                 # mix spellings (ai/ay, sh/ch ...) instead of listing one group first
        groups = {}
        for w in words:
            groups.setdefault(WB.classify(r["page"], w), []).append(w)
        mixed = []
        while any(groups.values()):
            for g in list(groups):
                if groups[g]:
                    mixed.append(groups[g].pop(0))
        words = mixed
    example = words[-1] if len(words) > 11 else words[0]
    rest = [w for w in words if w != example]
    a = rest[:10]
    b = [w for w in rest if w not in a][:4]
    c = [w for w in rest if w not in a and w not in b][:4]
    if len(b) < 4:
        rng = random.Random(r["page"])
        extra = [w for w in a if w not in b]
        rng.shuffle(extra)
        b += extra[:4 - len(b)]
    if len(c) < 4:
        rng = random.Random(r["page"] * 3)
        extra = [w for w in a if w not in c]
        rng.shuffle(extra)
        c += extra[:4 - len(c)]
    return example, a, b, c


def lesson_page(r):
    p, col = r["page"], r["color"]
    example, a, b, c = pick_words(r)
    r["eumga"] = (example, a, b, c)
    chips = "".join(f'<span class="chip"><b class="en">{html.escape(g)}</b><i>→</i>{html.escape(ja)}</span>'
                    for g, ja in chart(p, a + [example]))
    ex = item(p, "예", example, filled=True)
    items = "".join(item(p, i, w) for i, w in enumerate(a, 1))
    rev = "".join(reverse_item(p, i, w) for i, w in enumerate(b, 1))
    dic = "".join(f'''<div class="dl"><span class="num">{i}</span><span class="lab">영어</span><span class="wl"></span>
      <span class="lab">음가</span><span class="wl"></span><span class="lab">→</span><span class="wl s"></span></div>''' for i in range(1, 5))
    return f"""
<section class="page" style="--c:{col}">
  {head(f"음가 쓰기 {p:02d} · {html.escape(r['set'])} · " + (f"<span class='en'>{html.escape(r['sound'])}</span>"
        if len(r['sound']) <= 24 else html.escape(r['rule'].split('—')[0].strip())),
        "단어를 보고, 글자 아래 칸에 읽는 소리를 한글 음가로 쓰세요. 그리고 → 에 합쳐 읽은 소리를 쓰세요.", col, len(a))}
  <div class="row1"><div class="chart"><span class="lbl">오늘의 소리</span>{chips}</div>
    <div class="exbox">{ex}</div></div>
  <h3><span class="tag">음가 ①</span> 음가 쓰기 <small>① 글자마다 음가 쓰기 → ② 두 음절 이상이면 선 긋기 → ③ 합쳐 읽기</small></h3>
  <div class="grid">{items}</div>
  <h3><span class="tag">음가 ②</span> 음가 보고 영어 단어 쓰기 <small>한글 음가와 뜻을 보고 오늘 배운 철자로 써요.</small></h3>
  <div class="rgrid">{rev}</div>
  <h3 class="c3"><span class="tag">음가 ③</span> 듣고 쓰기 <small>선생님이 불러 주는 단어를 영어로 쓰고, 음가와 합쳐 읽기까지 써요. (불러 줄 단어는 정답지에)</small></h3>
  <div class="dgrid">{dic}</div>
  <div class="ft"><span>Phonics 음가 Workbook · {html.escape(r['set'])} {html.escape(WB.SETS[r['set']][0])}</span>
    <span>{html.escape(r['rule'])}</span><span>{p} 음가 / 42</span></div>
</section>"""


def test_page(set_name, srows):
    n = int(set_name[-1])
    col = WB.SETS[set_name][1]
    rng = random.Random(n * 4241)
    pool = []
    used = set()
    for r in srows:
        ws = [w for w in r["dict"] if w not in used]
        if ws:
            w = rng.choice(ws)
            used.add(w)
            pool.append((r["page"], w))
    rng.shuffle(pool)
    while len(pool) < 10:
        r = rng.choice(srows)
        w = rng.choice([w for w, _ in r["read"]])
        if w not in used:
            used.add(w)
            pool.append((r["page"], w))
    pool = pool[:10]
    items = "".join(f"""
    <div class="it"><div class="num">{i}</div><div class="body"><div class="cells">{word_cells(p, w, hl=False)}</div>
      <div class="rd">→ <span class="ln"></span></div></div></div>""" for i, (p, w) in enumerate(pool, 1))
    ex_cells = '<div class="gc"><div class="gl en">c</div><div class="jb fill">ㅋ</div></div>' \
               '<div class="gc"><div class="gl en">a</div><div class="jb fill">ㅐ</div></div>' \
               '<div class="gc"><div class="gl en">t</div><div class="jb fill">ㅌ</div></div>'
    page = f"""
<section class="page test" style="--c:{col}">
  {head(f"Phonics Test {n:02d} · {set_name} · {html.escape(WB.SETS[set_name][0])}",
        "단어를 보고, 아래 칸에 읽는 소리를 한글 음가로 쓰세요.", col)}
  <div class="tex"><span>예)</span><div class="cells">{ex_cells}</div><span class="arr">→ 캣</span></div>
  <div class="grid tg">{items}</div>
  <div class="ft"><span>Phonics 음가 Workbook · {set_name} Test</span><span>색 표시 없이 스스로!</span><span>Test {n}</span></div>
</section>"""
    return page, pool


def cover(rows):
    chips = []
    for s, (name, col) in WB.SETS.items():
        chips.append(f'<div class="cs" style="--c:{col}"><b>{s}</b><span>{name}</span></div>')
    return f"""
<section class="page cover">
  <h1 class="en">Phonics 음가 Workbook</h1>
  <div class="sub">글자 → 한글 음가 → 합쳐 읽기 · 42 Lessons · 5 Tests</div>
  <div class="demo">
    <div class="cells big">
      <div class="gc"><div class="gl en">s</div><div class="jb fill">ㅅ</div></div>
      <div class="gc"><div class="gl en">u</div><div class="jb fill">ㅓ</div></div>
      <div class="gc"><div class="gl en">n</div><div class="jb fill">ㄴ</div></div>
      <div class="cutline"></div>
      <div class="gc"><div class="gl en">s</div><div class="jb fill">ㅅ</div></div>
      <div class="gc"><div class="gl en">e</div><div class="jb fill">ㅔ</div></div>
      <div class="gc"><div class="gl en">t</div><div class="jb fill">ㅌ</div></div>
    </div>
    <div class="demo-ans">→ 선셋</div>
  </div>
  <div class="sets">{''.join(chips)}</div>
  <div class="name">이름 :</div><div class="name">반 :</div>
</section>"""


def guide(rows):
    master = []
    for s, (name, col) in WB.SETS.items():
        cells = []
        for r in [r for r in rows if r["set"] == s]:
            ch = " · ".join(f"<b class='en'>{html.escape(g)}</b> {html.escape(ja)}"
                            for g, ja in chart(r["page"], r["eumga"][1] + [r["eumga"][0]]))
            cells.append(f'<tr><td class="pg">{r["page"]}</td><td>{ch}</td></tr>')
        master.append(f'<div class="ms" style="--c:{col}"><div class="mh">{s} · {name}</div><table>{"".join(cells)}</table></div>')
    return f"""
<section class="page guide">
  <h1 class="pt">음가 쓰기 방법</h1>
  <div class="steps">
    <div class="st"><b>①</b> 글자(철자) 아래 칸에 <b>음가</b>를 써요. 두 글자가 한 소리(sh, ee, ck…)면 한 칸에 써요.</div>
    <div class="st"><b>②</b> 두 음절 이상이면 <b>선을 그어</b> 나눠요. (sun|set, rab|bit)</div>
    <div class="st"><b>③</b> → 에 <b>합쳐 읽은 소리</b>를 한글로 써요. (선셋, 래빗)</div>
    <div class="st"><b>기호</b> × 소리 없는 글자(Magic e, kn의 k) · <span class="en">r</span> 혀를 마는 r 소리(ar = ㅏr)</div>
  </div>
  <p class="note">짧은 모음 a=ㅐ e=ㅔ i=ㅣ o=ㅏ u=ㅓ · 긴 모음은 이름 소리(a=에이 i=아이 o=오우 u=유 e=이).
  받침: 짧은 모음 뒤 끝소리 t·k·p는 ㅅ·ㄱ·ㅂ 받침(cat 캣, duck 덕, cup 컵), n·m·l·ng는 받침(sun 선), 그 밖은 ㅡ를 붙여요(dog 다그, bus 버스).</p>
  <h2>전체 음가표</h2>
  <div class="master">{''.join(master)}</div>
</section>"""


def key(rows, tests):
    blocks = []
    for r in rows:
        ex, a, b, c = r["eumga"]
        def fmt(w, p=r["page"]):
            sy = syllables(p, w)
            cut = f" <i>({'|'.join(sy)})</i>" if len(sy) > 1 else ""
            return (f"<span class='w en'>{html.escape(w)}</span> {html.escape(' '.join(j for _, j in eumga(p, w)))}"
                    f" → <b>{html.escape(reading(p, w))}</b>{cut}")
        al = " &nbsp;·&nbsp; ".join(f"{i}. {fmt(w)}" for i, w in enumerate(a, 1))
        bl = ", ".join(f"{i}. <span class='en'>{html.escape(w)}</span>" for i, w in enumerate(b, 1))
        cl = " &nbsp;·&nbsp; ".join(f"{i}. {fmt(w)}" for i, w in enumerate(c, 1))
        blocks.append(f'<tr><td class="kp" style="color:{r["color"]}">{r["page"]}</td><td>① {al}<br>② {bl}<br>③ 불러 주기 — {cl}</td></tr>')
        if r["page"] in WB.SET_END:
            s = r["set"]
            tl = " &nbsp;·&nbsp; ".join(
                f"{i}. <span class='w en'>{html.escape(w)}</span> {html.escape(' '.join(j for _, j in eumga(p, w)))} → <b>{html.escape(reading(p, w))}</b>"
                for i, (p, w) in enumerate(tests[s], 1))
            blocks.append(f'<tr class="tr"><td class="kp">T{s[-1]}</td><td><b>{s} Test</b> — {tl}</td></tr>')
    pages, per = [], 7
    for i in range(0, len(blocks), per):
        pages.append(f"""
<section class="page"><h1 class="pt">정답 ({i // per + 1}) <small>합쳐 읽기는 학원 기준에 따라 조금 달라도 정답으로 인정해 주세요.</small></h1>
<table class="key">{''.join(blocks[i:i + per])}</table></section>""")
    return "".join(pages)


def build():
    rows = WB.load_rows()
    body, tests = [], {}
    lessons = []
    for r in rows:
        lessons.append(lesson_page(r))
        if r["page"] in WB.SET_END:
            pg, pool = test_page(r["set"], [x for x in rows if x["set"] == r["set"]])
            lessons.append(pg)
            tests[r["set"]] = pool
    body = [cover(rows), guide(rows)] + lessons + [key(rows, tests)]
    with open(CSS_FILE, encoding="utf-8") as f:
        css = f.read()
    doc = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>Phonics 음가 Workbook</title>
<link href="https://fonts.googleapis.com/css2?family=Andika:wght@400;700&family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
<style>{css}</style></head><body>{''.join(body)}</body></html>"""
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(doc)
    subprocess.run([
        WB.CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
        "--virtual-time-budget=20000", f"--print-to-pdf={OUT_PDF}", "file://" + OUT_HTML,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("wrote", OUT_HTML, OUT_PDF, file=sys.stderr)


if __name__ == "__main__":
    build()
