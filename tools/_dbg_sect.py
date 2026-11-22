import sys
sys.stdout.reconfigure(encoding="utf-8")
from docx import Document
from docx.oxml.ns import qn
d = Document(r"G:\compiler\reporet_2\0000000000--某某--编译原理--逆波兰式的翻译与求值--课设2.docx")
body = d.element.body
children = list(body)
print("children count:", len(children))
print("tags:", [c.tag.split('}')[1] for c in children][:30], "...")
for i, ch in enumerate(children):
    if ch.tag == qn("w:p"):
        ppr = ch.find(qn("w:pPr"))
        if ppr is not None and ppr.find(qn("w:sectPr")) is not None:
            # figure out which paragraph index
            idx = None
            for j, p in enumerate(d.paragraphs):
                if p._element is ch:
                    idx = j
                    break
            print(f"paragraph holding sectPr: children[{i}] = doc.paragraphs[{idx}]")
print("body-level sectPr present:", children[-1].tag == qn("w:sectPr"))
print("sections:", len(d.sections))
for k, s in enumerate(d.sections):
    print(f" section{k}: L{s.left_margin.cm:.2f} R{s.right_margin.cm:.2f} page {s.page_width.cm:.2f}x{s.page_height.cm:.2f}")
