# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
from docx import Document
from docx.oxml.ns import qn
d = Document(r"G:\compiler\reporet_2\0000000000--某某--编译原理--逆波兰式的翻译与求值--课设2.docx")
for i in (6,10,11,12,13,16,17,18):
    p = d.paragraphs[i]
    print(f"--- para {i}: style={p.style.name!r} align={p.alignment} text={p.text!r}")
    ppr = p._element.pPr
    print("    pPr:", ppr.xml.replace("\n","")[:200] if ppr is not None else None)
    for j,r in enumerate(p.runs):
        f = r.font
        print(f"    run{j}: text={r.text!r} sz={f.size.pt if f.size else None} name={f.name} bold={f.bold} underline={f.underline} color={f.color.rgb if f.color and f.color.rgb else None}")
        print("      rPr:", r._element.rPr.xml.replace("\n","")[:220] if r._element.rPr is not None else None)
