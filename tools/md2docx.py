# -*- coding: utf-8 -*-
"""
md2docx.py —— 把 report/*.md 渲染成符合课设模板格式的 docx。

设计原则
--------
1. 以老师模板 docx 为基底：保留封面、样式、节属性、页眉页脚；只清空正文并重填。
2. 正文格式全部显式写入 run/paragraph（不依赖 Word 样式表），因此换机器、换 Word
   版本都不会跑版。
3. Markdown 约定（见 report/报告写作约定.md）：
     # 标题          -> 一级标题  黑体 15pt 加粗
     ## 标题         -> 二级标题  黑体 12pt 加粗
     ### 标题        -> 三级标题  黑体 10.5pt 加粗
     普通段落        -> 正文 宋体 10.5pt / 20pt 固定行距 / 首行缩进 2 字符 / 两端对齐
     - 列表项        -> 悬挂列表
     > 注释          -> 红色提示段（定稿前应清空）
     ```代码```      -> 等宽 8.5pt + 灰底
     ![alt](path)    -> 居中插图
     图2-1 名称      -> 图题（居中，跟在图片后）
     表2-1 名称      -> 表题（居中，位于表格前）
     | a | b |       -> 9pt 表格，首行为表头
4. 生成后立刻做机器校验：字体字号行距、图表编号连号、每张图表是否被正文引用。

用法
----
    py -3.13 tools/md2docx.py report/草稿-报告二.md out/报告二-草稿.docx
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(
    ROOT, "0000000000--某某--编译原理--逆波兰式的翻译与求值--课设2.docx"
)
FIGS = os.path.join(ROOT, "figs")

# ---- 模板实测参数（见 out/template_structure.txt / probe_report.txt） ----
HEI, SONG, MONO = "黑体", "宋体", "Consolas"
LATIN = "Times New Roman"
H1_SIZE, H2_SIZE, H3_SIZE = Pt(15), Pt(12), Pt(10.5)   # 一级 15pt / 二级 12pt / 三级
BODY_SIZE = Pt(10.5)
LINE = Pt(20)
INDENT = Pt(21)
CAPTION_SIZE = Pt(10.5)
TABLE_SIZE = Pt(9)
CODE_SIZE = Pt(8.5)

COVER = {"学号": "0000000000", "姓名": "某某", "专业": "软件工程"}


# ------------------------------------------------------------------ 基础排版
def style_run(run, cn=SONG, size=BODY_SIZE, bold=False, latin=LATIN, color=None):
    run.font.name = latin
    run.font.size = size
    run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    rfonts.set(qn("w:ascii"), latin)
    rfonts.set(qn("w:hAnsi"), latin)
    rfonts.set(qn("w:eastAsia"), cn)


def set_pf(p, before=None, after=None, line=None, align=None, first_indent=None,
           left_indent=None, keep_next=False):
    pf = p.paragraph_format
    if before is not None:
        pf.space_before = before
    if after is not None:
        pf.space_after = after
    if line is not None:
        pf.line_spacing = line
    if align is not None:
        pf.alignment = align
    if first_indent is not None:
        pf.first_line_indent = first_indent
    if left_indent is not None:
        pf.left_indent = left_indent
    if keep_next:
        pf.keep_with_next = True


def shade(p, fill="F2F2F2"):
    ppr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    ppr.append(shd)


def add_bottom_border(p):
    ppr = p._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "808080")
    pbdr.append(bottom)
    ppr.append(pbdr)


def table_borders(table):
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement("w:" + edge)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "000000")
        borders.append(el)
    tbl_pr.append(borders)


# ------------------------------------------------------------------ 模板手术
def build_doc(md_path, out_path):
    import copy

    doc = Document(TPL)
    body = doc.element.body
    children = list(body)

    # 1) 模板里 cover+正文 属于同一个节，分节符在文末"其他说明"页（实测 children[115]）。
    #    策略：保留 [封面 + 正文标题]，删掉其后全部内容，并把该节的 sectPr
    #    （决定纸张/页边距/页眉页脚）搬到文档末尾，做到"单节、正文格式不变"。
    title_idx = None
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip().startswith("课程设计报告："):
            title_idx = i
            break
    if title_idx is None:
        raise RuntimeError("模板里找不到正文标题段（课程设计报告：…）")

    title_el = doc.paragraphs[title_idx]._element
    body_children = list(body)
    pos = body_children.index(title_el)

    sect_el = None
    for ch in body_children[pos + 1:]:
        if ch.tag == qn("w:p"):
            ppr = ch.find(qn("w:pPr"))
            if ppr is not None and ppr.find(qn("w:sectPr")) is not None:
                sect_el = copy.deepcopy(ppr.find(qn("w:sectPr")))
                break
    if sect_el is None:
        raise RuntimeError("模板里找不到正文节属性（sectPr）")

    for ch in body_children[pos + 1:]:
        body.remove(ch)
    body.append(sect_el)  # 单节文档：末尾 sectPr 决定全篇页面参数

    # 2) 填封面
    fill_cover(doc)

    # 3) 渲染 md
    stats = render_md(doc, md_path)

    doc.save(out_path)
    return stats


def fill_cover(doc):
    """把封面上的下划线空白处填上 学号/姓名/专业（保留模板原有的下划线格式）。"""
    targets = {"学    号：": "学号", "姓    名：": "姓名", "专    业：": "专业"}
    for p in doc.paragraphs[:20]:
        text = p.text
        key = next((k for k in targets if k in text), None)
        if key is None:
            continue
        value = COVER[targets[key]]
        # 找第一个带下划线且内容是空白的 run，填入值；不足则补空格保持行宽
        for r in p.runs:
            if r.font.underline and not r.text.strip():
                pad = max(0, len(r.text) - len(value) - 1)
                r.text = value + " " * pad
                break


# ------------------------------------------------------------------ Markdown 渲染
CAP_FIG = re.compile(r"^图\s*\d+-\d+")
CAP_TAB = re.compile(r"^表\s*\d+-\d+")
IMG_LINE = re.compile(r"^!\[[^\]]*\]\(([^)]+)\)\s*$")
CODE_FENCE = re.compile(r"^```")


class Ctx:
    def __init__(self):
        self.stats = {"para": 0, "fig": 0, "tab": 0, "code": 0, "h1": 0, "h2": 0}
        self.last_was_image = False


def add_h(doc, text, level):
    p = doc.add_paragraph()
    if level == 1:
        set_pf(p, before=Pt(12), after=Pt(6), line=LINE, keep_next=True)
        style_run(p.add_run(text), cn=HEI, size=H1_SIZE, bold=True)
    elif level == 2:
        set_pf(p, before=Pt(10), after=Pt(4), line=LINE, keep_next=True)
        style_run(p.add_run(text), cn=HEI, size=H2_SIZE, bold=True)
    else:
        set_pf(p, before=Pt(8), after=Pt(3), line=LINE, keep_next=True)
        style_run(p.add_run(text), cn=HEI, size=H3_SIZE, bold=True)
    return p


def add_body(doc, text, indent=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    set_pf(p, before=Pt(5.25), after=Pt(5.25), line=LINE, align=align,
           first_indent=INDENT if indent else None)
    style_run(p.add_run(text), cn=SONG, size=BODY_SIZE)
    return p


def add_list(doc, text):
    p = doc.add_paragraph()
    set_pf(p, before=Pt(2), after=Pt(2), line=LINE,
           align=WD_ALIGN_PARAGRAPH.JUSTIFY, left_indent=Pt(21))
    p.paragraph_format.first_line_indent = Pt(-10.5)
    style_run(p.add_run("· " + text), cn=SONG, size=BODY_SIZE)
    return p


def add_note(doc, text):
    p = doc.add_paragraph()
    set_pf(p, before=Pt(4), after=Pt(4), line=LINE,
           align=WD_ALIGN_PARAGRAPH.LEFT)
    style_run(p.add_run("【提示】" + text), cn=SONG, size=Pt(10.5),
              color=RGBColor(0xC0, 0x00, 0x00))
    return p


def add_caption(doc, text, above_table=False):
    p = doc.add_paragraph()
    if above_table:
        set_pf(p, before=Pt(10), after=Pt(3), align=WD_ALIGN_PARAGRAPH.CENTER,
               keep_next=True)
    else:
        set_pf(p, before=Pt(3), after=Pt(10), align=WD_ALIGN_PARAGRAPH.CENTER)
    style_run(p.add_run(text), cn=SONG, size=CAPTION_SIZE)
    return p


def add_image(doc, rel_path):
    full = os.path.join(FIGS, os.path.basename(rel_path))
    if not os.path.exists(full):
        raise FileNotFoundError("图片不存在: " + full)
    p = doc.add_paragraph()
    set_pf(p, before=Pt(8), after=Pt(2), align=WD_ALIGN_PARAGRAPH.CENTER,
           keep_next=True)
    width_cm = 14.5
    p.add_run().add_picture(full, width=Cm(width_cm))
    return p


def add_code(doc, lines, ctx):
    for i, line in enumerate(lines):
        p = doc.add_paragraph()
        set_pf(p, before=Pt(0), after=Pt(0), line=Pt(11),
               align=WD_ALIGN_PARAGRAPH.LEFT)
        shade(p)
        if i == 0:
            p.paragraph_format.space_before = Pt(6)
        if i == len(lines) - 1:
            p.paragraph_format.space_after = Pt(6)
        style_run(p.add_run(line if line else " "), cn=MONO, size=CODE_SIZE,
                  latin=MONO)
    ctx.stats["code"] += len(lines)


def add_table(doc, rows):
    ncol = max(len(r) for r in rows)
    table = doc.add_table(rows=0, cols=ncol)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_borders(table)
    for ridx, row in enumerate(rows):
        cells = table.add_row().cells
        for cidx in range(ncol):
            text = row[cidx] if cidx < len(row) else ""
            p = cells[cidx].paragraphs[0]
            for r in list(p.runs):
                r._element.getparent().remove(r._element)
            set_pf(p, before=Pt(2), after=Pt(2), line=Pt(13),
                   align=WD_ALIGN_PARAGRAPH.CENTER)
            style_run(p.add_run(text.replace("**", "")), cn=SONG, size=TABLE_SIZE,
                      bold=(ridx == 0))
    return table


def render_md(doc, md_path):
    ctx = Ctx()
    with open(md_path, encoding="utf-8") as f:
        lines = f.read().split("\n")

    i = 0
    n = len(lines)
    while i < n:
        raw = lines[i]
        line = raw.rstrip()

        if not line.strip():
            i += 1
            continue

        if CODE_FENCE.match(line):
            i += 1
            buf = []
            while i < n and not CODE_FENCE.match(lines[i]):
                buf.append(lines[i].rstrip())
                i += 1
            i += 1
            add_code(doc, buf, ctx)
            continue

        m = IMG_LINE.match(line.strip())
        if m:
            add_image(doc, m.group(1))
            ctx.stats["fig"] += 1
            ctx.last_was_image = True
            i += 1
            continue

        if line.startswith("# "):
            add_h(doc, line[2:].strip(), 1)
            ctx.stats["h1"] += 1
            ctx.last_was_image = False
            i += 1
            continue
        if line.startswith("## "):
            add_h(doc, line[3:].strip(), 2)
            ctx.stats["h2"] += 1
            ctx.last_was_image = False
            i += 1
            continue
        if line.startswith("### "):
            add_h(doc, line[4:].strip(), 3)
            ctx.last_was_image = False
            i += 1
            continue

        if line.startswith(">"):
            add_note(doc, line.lstrip("> ").strip())
            ctx.last_was_image = False
            i += 1
            continue

        if line.startswith("- "):
            add_list(doc, line[2:].strip())
            ctx.last_was_image = False
            i += 1
            continue

        if line.strip().startswith("|"):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            add_table(doc, rows)
            ctx.stats["tab"] += 1
            ctx.last_was_image = False
            continue

        if CAP_FIG.match(line.strip()) or CAP_TAB.match(line.strip()):
            add_caption(doc, line.strip(), above_table=bool(CAP_TAB.match(line.strip())))
            ctx.last_was_image = False
            i += 1
            continue

        # 普通段落：合并连续非空行
        buf = [line.strip()]
        i += 1
        while (i < n and lines[i].strip() and not lines[i].startswith(("#", "|", ">", "- ", "!", "```"))
               and not CAP_FIG.match(lines[i].strip()) and not CAP_TAB.match(lines[i].strip())):
            buf.append(lines[i].strip())
            i += 1
        add_body(doc, "".join(buf))
        ctx.stats["para"] += 1
        ctx.last_was_image = False

    return ctx.stats


# ------------------------------------------------------------------ 机器校验
def validate(docx_path, log_path):
    doc = Document(docx_path)
    out = []
    ok, bad = [], []

    def rec(tag, msg):
        out.append(f"[{tag}] {msg}")
        if tag == "OK":
            ok.append(msg)
        else:
            bad.append(msg)

    paras = doc.paragraphs
    texts = [p.text.strip() for p in paras]

    # --- 1. 字体/字号/行距抽样 ---
    def fmt(p):
        if not p.runs:
            return {}
        r = p.runs[0]
        rpr = r._element.rPr
        rf = rpr.find(qn("w:rFonts")) if rpr is not None else None
        sz = rpr.find(qn("w:sz")) if rpr is not None else None
        ppr = p._element.pPr
        sp = ppr.find(qn("w:spacing")) if ppr is not None else None
        ind = ppr.find(qn("w:ind")) if ppr is not None else None
        return {
            "ea": rf.get(qn("w:eastAsia")) if rf is not None else None,
            "sz": sz.get(qn("w:val")) if sz is not None else None,
            "line": sp.get(qn("w:line")) if sp is not None else None,
            "rule": sp.get(qn("w:lineRule")) if sp is not None else None,
            "first": ind.get(qn("w:firstLine")) if ind is not None else None,
            "jc": str(p.alignment),
        }

    h1 = next((p for p in paras if re.match(r"^1\s", p.text.strip())), None)
    body_p = next((p for p in paras if fmt(p).get("sz") == "21" and len(p.text) > 30), None)
    if body_p is not None:
        f = fmt(body_p)
        rec("OK" if f["ea"] == SONG else "FAIL", f"正文字体={f['ea']}")
        rec("OK" if f["sz"] == "21" else "FAIL", f"正文字号={f['sz']} (21 半点=10.5pt 五号)")
        rec("OK" if (f["line"], f["rule"]) == ("400", "exact") else "FAIL",
            f"正文行距={f['line']}/{f['rule']} (400=20pt 固定值)")
        rec("OK" if f["first"] == "420" else "FAIL", f"正文首行缩进={f['first']} (420=2字符)")
    if h1 is not None:
        f = fmt(h1)
        rec("OK" if f["ea"] == HEI and f["sz"] == "30" else "FAIL",
            f"一级标题={f['ea']}/{f['sz']} (15pt 黑体)")

    # --- 2. 图表编号连号 + 引用检查 ---
    cap_figs = [t for t in texts if CAP_FIG.match(t)]
    cap_tabs = [t for t in texts if CAP_TAB.match(t)]

    def check_series(caps, label):
        seen = {}
        for c in caps:
            m = re.match(rf"^{label}\s*(\d+)-(\d+)", c)
            chap, num = int(m.group(1)), int(m.group(2))
            seen.setdefault(chap, []).append(num)
        for chap, nums in sorted(seen.items()):
            expect = list(range(1, len(nums) + 1))
            rec("OK" if sorted(nums) == expect else "FAIL",
                f"第{chap}章 {label} 编号={'/'.join(map(str, nums))} 期望={'/'.join(map(str, expect))}")

    check_series(cap_figs, "图")
    check_series(cap_tabs, "表")

    body_text = "".join(
        t for t in texts if not CAP_FIG.match(t) and not CAP_TAB.match(t)
    )
    for c in cap_figs:
        num = re.match(r"^图\s*(\d+-\d+)", c).group(1)
        rec("OK" if f"图{num}" in body_text else "FAIL",
            f"图{num} 是否在正文被引用：{'是' if f'图{num}' in body_text else '否（模板要求必须有文字引用）'}")
    for c in cap_tabs:
        num = re.match(r"^表\s*(\d+-\d+)", c).group(1)
        rec("OK" if f"表{num}" in body_text else "FAIL",
            f"表{num} 是否在正文被引用：{'是' if f'表{num}' in body_text else '否（模板要求必须有文字引用）'}")

    # --- 3. 图/表位置检查：图题必须在图片段之后，表题必须在表格之前 ---
    for idx, p in enumerate(paras):
        t = p.text.strip()
        if CAP_FIG.match(t):
            prev = paras[idx - 1] if idx > 0 else None
            has_img = prev is not None and bool(prev._element.findall(".//" + qn("w:drawing")))
            rec("OK" if has_img else "FAIL", f"{t[:12]} 图题前是否为图片：" + ("是" if has_img else "否"))
        if CAP_TAB.match(t):
            nxt = paras[idx + 1] if idx + 1 < len(paras) else None
            # 表格在 body 中是独立元素，判断下一个 body 元素类型
            el = p._element.getnext()
            is_tbl = el is not None and el.tag == qn("w:tbl")
            rec("OK" if is_tbl else "FAIL", f"{t[:12]} 表题后是否为表格：" + ("是" if is_tbl else "否"))

    # --- 4. 字数统计 ---
    cjk = re.compile(r"[\u4e00-\u9fff]")
    total = sum(len(cjk.findall(t)) for t in texts)
    rec("OK", f"全文汉字数={total}")
    # 第 4 章（总结）字数
    chap4 = []
    inside = False
    for t in texts:
        if re.match(r"^4\s", t) or t.startswith("4  "):
            inside = True
        elif re.match(r"^5\s", t) or t.startswith("5  "):
            inside = False
        if inside:
            chap4.append(t)
    n4 = len(cjk.findall("".join(chap4)))
    rec("OK" if n4 >= 600 else "FAIL", f"第4章总结汉字数={n4}（要求≥600）")

    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
        f.write(f"\n\n结果: {len(ok)} 项通过, {len(bad)} 项失败\n")
    return len(ok), len(bad), out


if __name__ == "__main__":
    md = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "report", "草稿-报告二.md")
    out_docx = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "out", "报告二-草稿.docx")
    os.makedirs(os.path.dirname(out_docx), exist_ok=True)
    stats = build_doc(md, out_docx)
    print("渲染完成:", out_docx, stats)
    log = os.path.splitext(out_docx)[0] + "-校验.txt"
    nok, nbad, _ = validate(out_docx, log)
    print(f"校验: {nok} OK / {nbad} FAIL -> {log}")
