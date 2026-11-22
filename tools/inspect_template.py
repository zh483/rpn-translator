# -*- coding: utf-8 -*-
"""Dump the teacher's template structure: paragraph index, style, red runs, alignment."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

from docx import Document
from docx.shared import RGBColor

TPL = r"G:\compiler\reporet_2\0000000000--某某--编译原理--逆波兰式的翻译与求值--课设2.docx"
d = Document(TPL)

print("=== sections ===")
for s in d.sections:
    print(
        "page %.2fx%.2f cm | margins T%.2f B%.2f L%.2f R%.2f | header距%.2f footer距%.2f"
        % (
            s.page_width.cm, s.page_height.cm,
            s.top_margin.cm, s.bottom_margin.cm, s.left_margin.cm, s.right_margin.cm,
            s.header_distance.cm, s.footer_distance.cm,
        )
    )
    print("  不同首页/奇偶页: different_first_page=%s" % d.settings.odd_and_even_pages_header_footer)

print("\n=== paragraphs ===")
RED = RGBColor(0xFF, 0x00, 0x00)
for i, p in enumerate(d.paragraphs):
    txt = p.text.strip()
    reds = []
    sizes = []
    fonts = []
    bolds = []
    for r in p.runs:
        c = r.font.color
        if c is not None and c.rgb is not None:
            if str(c.rgb).upper().startswith("FF0000") or str(c.rgb).upper().startswith("C00000"):
                reds.append(r.text[:20])
        if r.font.size:
            sizes.append(r.font.size.pt)
        if r.font.name:
            fonts.append(r.font.name)
        if r.font.bold:
            bolds.append(True)
    if not txt and not reds:
        continue
    num = p._element.pPr.numPr if p._element.pPr is not None else None
    print(
        "%3d | %-14s | align=%-6s | num=%-3s | sz=%s | font=%s | bold=%s | red=%s | %s"
        % (
            i,
            p.style.name[:14],
            str(p.alignment)[:6] if p.alignment is not None else "-",
            "Y" if num is not None else "-",
            ",".join(str(x) for x in sorted(set(sizes))) or "-",
            ",".join(sorted(set(fonts))) or "-",
            "Y" if bolds else "-",
            ("RED:" + "|".join(reds)[:40]) if reds else "-",
            txt[:70],
        )
    )

print("\n=== tables ===", len(d.tables))
print("=== images ===", len(d.inline_shapes))
for sh in d.inline_shapes:
    print("  image %.2f x %.2f cm" % (sh.width.cm, sh.height.cm))
