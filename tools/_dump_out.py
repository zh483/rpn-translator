import sys
sys.stdout.reconfigure(encoding="utf-8")
from docx import Document
d = Document(r"out\报告二-草稿.docx")
for i,p in enumerate(d.paragraphs[:40]):
    t = p.text.strip()
    r0 = p.runs[0] if p.runs else None
    sz = r0.font.size.pt if (r0 and r0.font.size) else None
    nm = r0.font.name if r0 else None
    ea = None
    if r0 is not None and r0._element.rPr is not None:
        from docx.oxml.ns import qn
        rf = r0._element.rPr.find(qn("w:rFonts"))
        ea = rf.get(qn("w:eastAsia")) if rf is not None else None
    print(f"{i:3d} | sz={sz} | latin={nm} | ea={ea} | {t[:60]}")
print("total paragraphs:", len(d.paragraphs))
