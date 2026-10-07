"""Build the combined workbook: lesson pages + 음가 쓰기 pages in one PDF.

Usage:
    python workbook/build_combined.py     # writes workbook/phonics_combined_workbook.html + .pdf

Per sound: A 배우기 → 음가 쓰기 → B 연습 → C 쓰기.
Per set:   총복습 2쪽 → Phonics Test.
Front: 표지 · 공부 방법 · 음가 쓰기 방법/음가표 · 목차.  Back: 정답(학습지) · 정답(음가·테스트).
The two stylesheets are scoped (.wb / .eg) so their class names cannot collide.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_workbook as WB  # noqa: E402
import build_eumga as EG  # noqa: E402
import cover as CV  # noqa: E402

COVER = os.environ.get("COVER", "v3")   # v1 | v2 | v3 — see cover.py / cover_preview.pdf

OUT_HTML = os.path.join(HERE, "phonics_combined_workbook.html")
OUT_PDF = os.path.join(HERE, "phonics_combined_workbook.pdf")
GLOBAL = {"html", "body", "*", "html, body"}


def scope_css(css, prefix):
    """Prefix every selector with prefix (leaving @page and global resets alone)."""
    out = []
    for block in re.findall(r"[^{}]+\{[^{}]*\}", css):
        sel, body = block.split("{", 1)
        sel = sel.strip()
        if sel.startswith("@") or sel in GLOBAL:
            out.append(f"{sel} {{{body}")
            continue
        sels = ", ".join(f"{prefix} {s.strip()}" for s in sel.split(","))
        out.append(f"{sels} {{{body}")
    return "\n".join(out)


def patch(text, old, new):
    assert old in text, old[:60]
    return text.replace(old, new)


def wb(html):
    return f'<div class="wb">{html}</div>'


def eg(html):
    return f'<div class="eg">{html}</div>'


FRONT = 5          # cover, tracker, guide, 음가 guide, contents
PAGE_NUM_CSS = """
body { counter-reset: pg; }
section.cv, .wb section.page, .eg section.page { counter-increment: pg; }
.wb section.page::after, .eg section.page::after { content: counter(pg); position: absolute; bottom: 2.6mm; left: 0; right: 0;
  text-align: center; font: 700 7.5pt 'Noto Sans KR', sans-serif; color: #9aa3b5; }
"""


def start_page(page):
    """Physical page where lesson `page` (1-42) starts: 4 pages per lesson, +3 after each set."""
    sets_done = sum(1 for e in WB.SET_END if e < page)
    return FRONT + 1 + 4 * (page - 1) + 3 * sets_done


def contents(rows):
    trs = []
    for r in rows:
        p = r["page"]
        sp = start_page(p)
        trs.append(
            f'<tr><td>{p}</td><td><span class="chip" style="background:{r["color"]}">{r["set"]}</span></td>'
            f'<td class="snd en" style="color:{r["color"]}">{WB.html.escape(r["sound"])}</td>'
            f'<td>{WB.html.escape(r["rule"])}</td><td class="pn">{sp}</td></tr>')
        if p in WB.SET_END:
            trs.append(f'<tr class="rvrow"><td></td><td colspan="3">↳ {r["set"]} 총복습 2쪽 + Phonics Test</td>'
                       f'<td class="pn">{sp + 4}</td></tr>')
    key_start = start_page(42) + 4 + 3
    trs.append(f'<tr class="rvrow"><td></td><td colspan="3">정답 · 불러 주기 · 음가 정답</td><td class="pn">{key_start}</td></tr>')
    return f"""
<section class="page"><h1 class="pt">목차 <small>각 소리는 A 배우기 → 음가 쓰기 → B 연습 → C 쓰기 (4쪽)</small></h1>
<table class="toc"><tr><th>단계</th><th>세트</th><th>소리</th><th>묶음 기준</th><th>쪽</th></tr>{''.join(trs)}</table></section>"""


def build():
    rows = WB.build_lesson_data(WB.load_rows())
    reviews = WB.build_reviews(rows)

    lessons, tests = [], {}
    for r in rows:
        eg_page = EG.lesson_page(r)                       # also stores r["eumga"] for the key
        lessons += [wb(WB.page_a(r)), eg(eg_page), wb(WB.page_b(r)), wb(WB.page_c(r))]
        if r["page"] in WB.SET_END:
            lessons.append(wb(WB.review_pages(r["set"], reviews[r["set"]])))
            pg, pool = EG.test_page(r["set"], [x for x in rows if x["set"] == r["set"]])
            lessons.append(eg(pg))
            tests[r["set"]] = pool

    n_words = sum(len(r["read"]) for r in rows)
    cover = getattr(CV, f"cover_{COVER}")(n_words, 0) + CV.tracker(rows)

    guide = WB.guide()
    guide = patch(guide, "<h3>하루 10~15분, 한 소리를 사흘에 걸쳐</h3>",
                  "<h3>하루 10~15분, 한 소리를 사흘에 걸쳐 (1일차는 A + 음가 쓰기)</h3>")
    guide = patch(guide, "<tr><td>2일차</td>",
                  "<tr><td>1일차</td><td><b>음가 쓰기</b></td><td>글자마다 한글 음가 → 음절 선 긋기 → 합쳐 읽기 · 음가 보고 영어 쓰기 · 듣고 쓰기</td>"
                  "<td>소리를 한글 음가로 확인하며 철자-소리 연결을 굳혀요.</td></tr>\n    <tr><td>2일차</td>")
    guide = patch(guide, "섞어 읽기 · 철자 고르기 · 받아쓰기 · 낱말 찾기 · 실력 체크",
                  "섞어 읽기 · 철자 고르기 · 받아쓰기 · 낱말 찾기 · 실력 체크 → <b>Phonics Test</b>(음가 10문항)")

    toc = contents(rows)

    body = [cover, wb(guide), eg(EG.guide(rows)), wb(toc)] + lessons + [
        wb(WB.key(rows, reviews)), eg(EG.key(rows, tests))]

    css = [CV.CSS, PAGE_NUM_CSS]
    for path, prefix in ((WB.CSS_FILE, ".wb"), (EG.CSS_FILE, ".eg")):
        with open(path, encoding="utf-8") as f:
            css.append(scope_css(f.read(), prefix))
    doc = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>Phonics Workbook (통합본)</title>
<link href="https://fonts.googleapis.com/css2?family=Andika:wght@400;700&family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
<style>{''.join(css)}</style></head><body>{''.join(body)}</body></html>"""
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(doc)
    subprocess.run([
        WB.CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
        "--virtual-time-budget=30000", f"--print-to-pdf={OUT_PDF}", "file://" + OUT_HTML,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("wrote", OUT_HTML, OUT_PDF, file=sys.stderr)


if __name__ == "__main__":
    build()
