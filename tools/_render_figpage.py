import sys, pymupdf
sys.stdout.reconfigure(encoding="utf-8")
d = pymupdf.open(r"out\报告二-草稿.pdf")
for i in range(d.page_count):
    t = d[i].get_text()
    for k in ("图2-1", "图2-2", "图3-1", "图3-2"):
        if k in t and ("系统功能模块图" in t or "流程图" in t or "界面" in t):
            pix = d[i].get_pixmap(dpi=110)
            p = rf"out\preview-fig-{k}-p{i+1}.png"
            pix.save(p)
            print(k, "->", p)
