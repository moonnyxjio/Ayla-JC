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

    cover = WB.cover(rows)
    cover = patch(cover, "<i>A B C</i>", "<i>A 음 B C</i>")
    cover = patch(cover, "진도표 — 끝낸 A·B·C에 색칠하거나", "진도표 — 끝낸 A·음가·B·C에 색칠하거나")
    cover = cover.replace("복습</span>", "복습·Test</span>")

    guide = WB.guide()
    guide = patch(guide, "<h3>하루 10~15분, 한 소리를 사흘에 걸쳐</h3>",
                  "<h3>하루 10~15분, 한 소리를 사흘에 걸쳐 (1일차는 A + 음가 쓰기)</h3>")
    guide = patch(guide, "<tr><td>2일차</td>",
                  "<tr><td>1일차</td><td><b>음가 쓰기</b></td><td>글자마다 한글 음가 → 음절 선 긋기 → 합쳐 읽기 · 음가 보고 영어 쓰기 · 듣고 쓰기</td>"
                  "<td>소리를 한글 음가로 확인하며 철자-소리 연결을 굳혀요.</td></tr>\n    <tr><td>2일차</td>")
    guide = patch(guide, "섞어 읽기 · 철자 고르기 · 받아쓰기 · 낱말 찾기 · 실력 체크",
                  "섞어 읽기 · 철자 고르기 · 받아쓰기 · 낱말 찾기 · 실력 체크 → <b>Phonics Test</b>(음가 10문항)")

    toc = WB.toc(rows)
    toc = patch(toc, "각 소리는 A(배우기)·B(연습)·C(쓰기) 3쪽", "각 소리는 A(배우기)·음가 쓰기·B(연습)·C(쓰기) 4쪽")
    toc = toc.replace("총복습 (2쪽)", "총복습 (2쪽) + Phonics Test")

    body = [wb(cover), wb(guide), eg(EG.guide(rows)), wb(toc)] + lessons + [
        wb(WB.key(rows, reviews)), eg(EG.key(rows, tests))]

    css = []
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
