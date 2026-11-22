import sys, fitz
sys.stdout.reconfigure(encoding="utf-8")
d = fitz.open(r"out\报告二-草稿.pdf")
print("pages:", d.page_count)
for i in range(min(4, d.page_count)):
    pix = d[i].get_pixmap(dpi=110)
    p = rf"out\preview-p{i+1}.png"
    pix.save(p)
    print("saved", p, pix.width, "x", pix.height)
# 找含表格的页
for i in range(d.page_count):
    t = d[i].get_text()
    if "表2-5" in t:
        pix = d[i].get_pixmap(dpi=110); p = rf"out\preview-table-p{i+1}.png"; pix.save(p)
        print("table page", i+1, p); break
