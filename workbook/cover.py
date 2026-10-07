"""Cover designs for the combined workbook (+ the progress tracker page that used to live on the cover).

    python workbook/cover.py        # renders workbook/cover_preview.pdf with all three designs
"""
import html
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_workbook as WB  # noqa: E402

SET_COLORS = [c for _, c in WB.SETS.values()]
TILES = [("a", "Set 1"), ("sh", "Set 2"), ("ee", "Set 3"), ("ar", "Set 4"), ("tion", "Set 5")]

CSS = """
.cv, .cv * { box-sizing: border-box; }
.cv { width: 210mm; height: 297mm; position: relative; overflow: hidden; page-break-after: always;
  font-family: 'Noto Sans KR', sans-serif; color: #1F2A44; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.cv .en { font-family: 'Andika', sans-serif; }

/* ---------- v1: navy panel + toy blocks ---------- */
.v1 { background: #FFF8EC; }
.v1 .panel { position: absolute; left: 0; top: 0; width: 210mm; height: 158mm; background: #1F2A44; }
.v1 .wave { position: absolute; left: 0; top: 150mm; width: 210mm; height: 30mm; }
.v1 .dots { position: absolute; inset: 0 0 auto 0; height: 150mm; opacity: .10;
  background-image: radial-gradient(#fff 1.1px, transparent 1.2px); background-size: 7mm 7mm; }
.v1 .kick { position: absolute; left: 18mm; top: 22mm; color: #FFC93C; font-weight: 700; font-size: 11pt; letter-spacing: 2.5mm; }
.v1 h1 { position: absolute; left: 16mm; top: 30mm; margin: 0; color: #fff; font-size: 74pt; line-height: 1; font-weight: 700; letter-spacing: -.5mm; }
.v1 h1 span { color: #FFC93C; }
.v1 .sub { position: absolute; left: 18mm; top: 62mm; color: #fff; font-size: 21pt; font-weight: 900; }
.v1 .sub2 { position: absolute; left: 18mm; top: 76mm; color: #B9C3D9; font-size: 11pt; }
.v1 .blocks { position: absolute; left: 14mm; right: 14mm; top: 104mm; display: flex; justify-content: space-between; }
.v1 .blk { width: 33mm; height: 33mm; border-radius: 6mm; display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 30pt; font-weight: 700; box-shadow: 0 2.2mm 0 rgba(0,0,0,.22); position: relative; }
.v1 .blk small { position: absolute; bottom: -7mm; left: 0; right: 0; text-align: center; font-family: 'Noto Sans KR';
  font-size: 8.5pt; font-weight: 700; color: #fff; opacity: .85; }
.v1 .demo { position: absolute; left: 50%; transform: translateX(-50%); top: 178mm; display: flex; align-items: center; gap: 4mm;
  background: #fff; border-radius: 12mm; padding: 4mm 9mm; box-shadow: 0 1mm 4mm rgba(31,42,68,.12); white-space: nowrap; }
.v1 .demo .w { font-size: 24pt; font-weight: 700; letter-spacing: 2mm; }
.v1 .demo .j { display: flex; gap: 1.2mm; }
.v1 .demo .j b { width: 10mm; height: 10mm; border: 0.5mm solid #2E86AB; border-radius: 2mm; display: flex; align-items: center;
  justify-content: center; color: #2E86AB; font-size: 14pt; }
.v1 .demo .arr { color: #9AA3B5; font-size: 16pt; }
.v1 .demo .k { font-size: 22pt; font-weight: 900; color: #E4572E; }
.v1 .path { position: absolute; left: 22mm; right: 22mm; top: 209mm; display: flex; justify-content: space-between; }
.v1 .path::before { content: ""; position: absolute; left: 8mm; right: 8mm; top: 7.5mm; border-top: 0.7mm dashed #C9D0DC; }
.v1 .st { position: relative; width: 30mm; text-align: center; }
.v1 .st i { display: flex; margin: 0 auto 1.5mm; width: 15mm; height: 15mm; border-radius: 50%; color: #fff; font-style: normal;
  align-items: center; justify-content: center; font-weight: 900; font-size: 12pt; border: 1.2mm solid #FFF8EC; }
.v1 .st span { font-size: 8pt; color: #4A5468; line-height: 1.25; display: block; }
.v1 .card { position: absolute; left: 30mm; right: 30mm; top: 241mm; background: #fff; border-radius: 4mm; padding: 4mm 8mm;
  box-shadow: 0 1mm 4mm rgba(31,42,68,.10); }
.v1 .card div { display: flex; gap: 4mm; align-items: flex-end; font-size: 11pt; font-weight: 700; height: 10mm; }
.v1 .card div span { flex: 1; border-bottom: 0.4mm solid #C9D0DC; height: 7mm; }
.v1 .foot { position: absolute; left: 0; right: 0; bottom: 8mm; text-align: center; font-size: 8.5pt; color: #8A93A6; letter-spacing: .6mm; }

/* ---------- v2: alphabet wall + center card ---------- */
.v2 { background: #fff; }
.v2 .wall { position: absolute; inset: -6mm; display: grid; grid-template-columns: repeat(7, 1fr); gap: 3mm; transform: rotate(-8deg) scale(1.15); }
.v2 .wall b { aspect-ratio: 1; border-radius: 4mm; display: flex; align-items: center; justify-content: center; font-family: 'Andika';
  font-size: 30pt; color: #fff; opacity: .9; }
.v2 .shade { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(255,255,255,.0) 0%, rgba(255,255,255,.55) 100%); }
.v2 .card { position: absolute; left: 22mm; right: 22mm; top: 72mm; background: #fff; border-radius: 8mm; padding: 14mm 12mm 12mm;
  box-shadow: 0 3mm 10mm rgba(31,42,68,.25); text-align: center; }
.v2 .card .kick { font-size: 10pt; letter-spacing: 2mm; color: #E4572E; font-weight: 700; }
.v2 .card h1 { margin: 2mm 0 0; font-size: 60pt; line-height: 1; }
.v2 .card .sub { font-size: 17pt; font-weight: 900; margin-top: 4mm; }
.v2 .card .sets { display: flex; justify-content: center; gap: 2mm; margin: 8mm 0 9mm; }
.v2 .card .sets span { color: #fff; border-radius: 3mm; padding: 1mm 3mm; font-size: 8.5pt; font-weight: 700; }
.v2 .card .ln { display: flex; gap: 3mm; align-items: flex-end; text-align: left; font-weight: 700; font-size: 11pt; margin: 0 6mm 4mm; }
.v2 .card .ln span { flex: 1; border-bottom: 0.4mm solid #C9D0DC; height: 7mm; }

/* ---------- v3: set stripes, editorial ---------- */
.v3 { background: #F7F4EF; }
.v3 .stripes { position: absolute; left: 0; top: 0; bottom: 0; width: 62mm; display: flex; flex-direction: column; }
.v3 .stripes div { flex: 1; display: flex; flex-direction: column; justify-content: center; padding-left: 9mm; color: #fff; }
.v3 .stripes b { font-family: 'Andika'; font-size: 34pt; line-height: 1; }
.v3 .stripes span { font-size: 8pt; opacity: .9; margin-top: 1.5mm; }
.v3 .stripes .dim { opacity: .28; }
.v3 h1 .bk { font-size: 64pt; }
.v3 .main { position: absolute; left: 76mm; right: 14mm; top: 34mm; }
.v3 .kick { font-size: 10pt; letter-spacing: 2mm; color: #8A93A6; font-weight: 700; }
.v3 h1 { margin: 4mm 0 0; font-size: 54pt; line-height: .95; }
.v3 .sub { font-size: 16pt; font-weight: 900; margin-top: 7mm; line-height: 1.45; }
.v3 .rule { width: 18mm; border-top: 1.4mm solid #E4572E; margin: 9mm 0; }
.v3 .feat { font-size: 10pt; line-height: 2; color: #4A5468; }
.v3 .feat b { color: #1F2A44; }
.v3 .ln { position: absolute; left: 76mm; right: 14mm; display: flex; gap: 3mm; align-items: flex-end; font-weight: 700; font-size: 11pt; }
.v3 .ln span { flex: 1; border-bottom: 0.4mm solid #1F2A44; height: 7mm; }

/* ---------- tracker page ---------- */
.trk { background: #fff; padding: 14mm 14mm; display: flex; flex-direction: column; }
.trk h2 { font-size: 18pt; margin: 0 0 1mm; }
.trk p { margin: 0 0 7mm; color: #6B7487; font-size: 9.5pt; }
.trk .set { border: 0.4mm solid var(--c); border-radius: 4mm; padding: 4mm 5mm; margin-bottom: 5mm; }
.trk .set h3 { margin: 0 0 3mm; color: var(--c); font-size: 11.5pt; }
.trk .set h3 small { color: #8A93A6; font-weight: 400; font-size: 8.5pt; margin-left: 2mm; }
.trk .row { display: flex; flex-wrap: wrap; gap: 2.4mm; }
.trk .ls { width: 16.4mm; border: 0.3mm solid #DFE3EA; border-radius: 2.5mm; padding: 1.2mm 0 1.5mm; text-align: center; }
.trk .ls b { display: block; font-size: 10pt; color: var(--c); }
.trk .ls span { display: flex; justify-content: center; gap: .8mm; margin-top: 1mm; }
.trk .ls span i { width: 3mm; height: 3mm; border-radius: 50%; border: 0.3mm solid #B6BDCA; font-style: normal; }
.trk .ls.t { background: color-mix(in srgb, var(--c) 10%, #fff); border-color: var(--c); }
.trk .ls.t b { font-size: 8pt; }
.trk .key { font-size: 8.5pt; color: #6B7487; margin-top: auto; }
"""


def blocks():
    return "".join(f'<div class="blk en" style="background:{c};transform:rotate({r}deg)">{t}<small>{s}</small></div>'
                   for (t, s), c, r in zip(TILES, SET_COLORS, (-6, 4, -3, 5, -4)))


def cover_v1(n_words, n_pages):
    steps = "".join(f'<div class="st"><i style="background:{c}">{k + 1}</i><span>{html.escape(name)}</span></div>'
                    for k, ((name, c)) in enumerate(WB.SETS.values()))
    return f"""
<section class="cv v1">
  <div class="panel"><div class="dots"></div></div>
  <svg class="wave" viewBox="0 0 210 30" preserveAspectRatio="none"><path d="M0 0 H210 V8 C160 30 120 0 70 16 C40 26 15 18 0 12 Z" fill="#1F2A44"/></svg>
  <div class="kick">PHONICS WORKBOOK</div>
  <h1 class="en">Phonics<span>.</span></h1>
  <div class="sub">소리로 읽고, 음가로 쓰는 파닉스</div>
  <div class="sub2">배우기 · 음가 쓰기 · 연습 · 쓰기 — 42개의 소리를 4단계로</div>
  <div class="blocks">{blocks()}</div>
  <div class="demo"><span class="w en">cat</span><span class="arr">→</span>
    <span class="j"><b>ㅋ</b><b>ㅐ</b><b>ㅌ</b></span><span class="arr">→</span><span class="k">캣</span></div>
  <div class="path">{steps}</div>
  <div class="card"><div>Name<span></span></div><div>Class<span></span></div></div>
  <div class="foot">5 SETS · 42 LESSONS · 5 TESTS · {n_words} WORDS</div>
</section>"""


def cover_v2(n_words, n_pages):
    letters = "abcdefghijklmnopqrstuvwxyz" * 3
    wall = "".join(f'<b style="background:{SET_COLORS[i % 5]}">{ch}</b>' for i, ch in enumerate(letters[:70]))
    sets = "".join(f'<span style="background:{c}">{s}</span>' for s, (_, c) in WB.SETS.items())
    return f"""
<section class="cv v2">
  <div class="wall">{wall}</div><div class="shade"></div>
  <div class="card">
    <div class="kick">PHONICS WORKBOOK</div>
    <h1 class="en">Phonics</h1>
    <div class="sub">소리로 읽고, 음가로 쓰는 파닉스</div>
    <div class="sets">{sets}</div>
    <div class="ln">Name<span></span></div><div class="ln">Class<span></span></div>
  </div>
</section>"""


def cover_v3(n_words, n_pages, vol=None, n_lessons=42):
    """vol=None: the whole book. vol=1..5: that Set's volume (its stripe stays bright, the others fade)."""
    stripes = "".join(f'<div class="{"dim" if vol and k != vol else ""}" style="background:{c}"><b>{t}</b>'
                      f'<span>{s} · {html.escape(name)}</span></div>'
                      for k, ((t, s), (name, c)) in enumerate(zip(TILES, WB.SETS.values()), 1))
    if vol:
        name, col = list(WB.SETS.values())[vol - 1]
        title = f'Phonics<br>Workbook <span class="bk" style="color:{col}">{vol}</span>'
        sub = f"Set {vol} · {html.escape(name)}"
        feat = (f"<b>{n_lessons}</b>개의 소리 · <b>4</b>단계 학습<br><b>1</b>회 Phonics Test<br>"
                f"<b>{n_words}</b>개 단어 · 그림 · QR 발음")
    else:
        title, sub = "Phonics<br>Workbook", "소리로 읽고,<br>음가로 쓰는 파닉스"
        feat = f"<b>42</b>개의 소리 · <b>4</b>단계 학습<br><b>5</b>회 Phonics Test<br><b>{n_words}</b>개 단어 · 그림 · QR 발음"
    return f"""
<section class="cv v3">
  <div class="stripes en">{stripes}</div>
  <div class="main">
    <div class="kick">PHONICS WORKBOOK</div>
    <h1 class="en">{title}</h1>
    <div class="sub">{sub}</div>
    <div class="rule"></div>
    <div class="feat">{feat}</div>
  </div>
  <div class="ln" style="top:236mm">Name<span></span></div>
  <div class="ln" style="top:250mm">Class<span></span></div>
</section>"""


def tracker(rows):
    sets = []
    for s, (name, col) in WB.SETS.items():
        if not any(r["set"] == s for r in rows):
            continue
        cells = "".join(
            f'<div class="ls"><b>{r["page"]}</b><span><i></i><i></i><i></i><i></i></span></div>'
            for r in rows if r["set"] == s)
        cells += '<div class="ls t"><b>복습<br>Test</b></div>'
        first, last = [r["page"] for r in rows if r["set"] == s][::len([r for r in rows if r["set"] == s]) - 1]
        sets.append(f'<div class="set" style="--c:{col}"><h3>{s} · {html.escape(name)}<small>{first}–{last}</small></h3>'
                    f'<div class="row">{cells}</div></div>')
    return f"""
<section class="cv trk">
  <h2>나의 진도표</h2>
  <p>한 소리를 끝낼 때마다 동그라미 4개(A 배우기 · 음가 쓰기 · B 연습 · C 쓰기)를 차례로 칠하거나 스티커를 붙여요.</p>
  {''.join(sets)}
  <div class="key">○○○○ = A · 음가 · B · C &nbsp;&nbsp; 복습·Test = Set 총복습 2쪽 + Phonics Test</div>
</section>"""


def preview():
    rows = WB.load_rows()
    n_words = sum(len(r["read"]) for r in rows)
    doc = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Andika:wght@400;700&family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
<style>@page{{size:A4;margin:0}} html,body{{margin:0}} {CSS}</style></head><body>
{cover_v1(n_words, 0)}{cover_v2(n_words, 0)}{cover_v3(n_words, 0)}{tracker(rows)}</body></html>"""
    out_html = os.path.join(HERE, "cover_preview.html")
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(doc)
    subprocess.run([WB.CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=15000", f"--print-to-pdf={os.path.join(HERE, 'cover_preview.pdf')}",
                    "file://" + out_html], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    preview()
