# -*- coding: utf-8 -*-
"""preview_pdf.py —— 把生成的 PDF 渲染成 PNG，用于人工检查排版。

用法:
    py -3.13 tools/preview_pdf.py                # 渲染 out/报告二-草稿.pdf 全部页
    py -3.13 tools/preview_pdf.py 3 7            # 只渲染第 3、7 页
输出: out/preview-p{N}.png
"""
import glob
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")

if len(sys.argv) > 1 and not sys.argv[1].isdigit():
    path = os.path.join(OUT, sys.argv[1])
    pages = [int(x) for x in sys.argv[2:]] or None
else:
    path = os.path.join(OUT, "报告二-草稿.pdf")
    pages = [int(x) for x in sys.argv[1:]] or None

if not os.path.exists(path):
    cands = glob.glob(os.path.join(OUT, "*.pdf"))
    print("找不到目标 PDF，out/ 下现有：", cands)
    sys.exit(1)

doc = pymupdf.open(path)
print(f"file={os.path.basename(path)} pages={doc.page_count} "
      f"size={doc[0].rect.width:.0f}x{doc[0].rect.height:.0f}pt")
for n in (pages if pages else range(1, doc.page_count + 1)):
    if not (1 <= n <= doc.page_count):
        continue
    pix = doc[n - 1].get_pixmap(dpi=110)
    out = os.path.join(OUT, f"preview-p{n}.png")
    pix.save(out)
    print("saved", os.path.basename(out))
