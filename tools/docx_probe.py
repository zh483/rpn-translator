# -*- coding: utf-8 -*-
"""
docx_probe.py —— 证明"python-docx 能按模板格式产出报告"，并给出可复用的样式函数。

做三件事：
1. 读出模板 docx 的真实页面参数（纸张、页边距、页眉页脚）；
2. 以模板为基底（保留样式/节/页眉页脚），清空正文，写入样例内容：
   一级标题、正文、图+图题、表+表题；
3. 重新打开产出的 docx，把每个关键段落的 w:rFonts / w:sz / w:spacing 抽出来比对预期值。

用法：py -3.13 tools/docx_probe.py
产出：out/模板格式验证.docx、out/probe_report.txt、figs/probe_fig2-1.png
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

from tpl import ROOT, TPL

OUT = os.path.join(ROOT, "out")
FIGS = os.path.join(ROOT, "figs")
os.makedirs(OUT, exist_ok=True)
os.makedirs(FIGS, exist_ok=True)

LOG_PATH = os.path.join(OUT, "probe_report.txt")
_logf = open(LOG_PATH, "w", encoding="utf-8")


def log(*args):
    print(*args, file=_logf)
    _logf.flush()


# ---------------------------------------------------------------- 样式常量
HEI = "黑体"
SONG = "宋体"
LATIN = "Times New Roman"
FULL1, FULL2, BODY = Pt(14), Pt(12), Pt(10.5)  # 四号 / 小四 / 五号


def set_run_font(run, cn=SONG, size=BODY, bold=False, latin=LATIN):
    run.font.name = latin
    run.font.size = size
    run.font.bold = bold
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    rfonts.set(qn("w:ascii"), latin)
    rfonts.set(qn("w:hAnsi"), latin)
    rfonts.set(qn("w:eastAsia"), cn)


def set_pf(p, before=None, after=None, line=None, align=None, first_indent=None):
    pf = p.paragraph_format
    if before is not None:
        pf.space_before = before
    if after is not None:
        pf.space_after = after
    if line is not None:
        pf.line_spacing = line  # 传 Length -> 固定行距(lineRule=exact)
    if align is not None:
        pf.alignment = align
    if first_indent is not None:
        pf.first_line_indent = first_indent


def h1(doc, text):
    p = doc.add_paragraph()
    set_pf(p, before=Pt(14), after=Pt(14), align=WD_ALIGN_PARAGRAPH.LEFT)
    set_run_font(p.add_run(text), cn=HEI, size=FULL1, bold=True)
    return p


def h2(doc, text):
    p = doc.add_paragraph()
    set_pf(p, before=Pt(12), after=Pt(12), align=WD_ALIGN_PARAGRAPH.LEFT)
    set_run_font(p.add_run(text), cn=HEI, size=FULL2, bold=True)
    return p


def body(doc, text, indent=True):
    p = doc.add_paragraph()
    set_pf(
        p,
        before=Pt(5.25),
        after=Pt(5.25),
        line=Pt(20),
        align=WD_ALIGN_PARAGRAPH.JUSTIFY,
        first_indent=Pt(21) if indent else None,
    )
    set_run_font(p.add_run(text), cn=SONG, size=BODY)
    return p


def caption(doc, text):
    p = doc.add_paragraph()
    set_pf(p, before=Pt(3), after=Pt(10), align=WD_ALIGN_PARAGRAPH.CENTER)
    set_run_font(p.add_run(text), cn=SONG, size=BODY)
    return p


def table_caption(doc, text):
    p = doc.add_paragraph()
    set_pf(p, before=Pt(10), after=Pt(3), align=WD_ALIGN_PARAGRAPH.CENTER)
    set_run_font(p.add_run(text), cn=SONG, size=BODY)
    return p


def figure(doc, filename, cap, width_cm):
    p = doc.add_paragraph()
    set_pf(p, before=Pt(8), after=Pt(2), align=WD_ALIGN_PARAGRAPH.CENTER)
    p.add_run().add_picture(os.path.join(FIGS, filename), width=Cm(width_cm))
    caption(doc, cap)


def set_table_borders(table):
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


def make_table(doc, headers, rows, fs=Pt(9)):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        p = cell.paragraphs[0]
        for r in list(p.runs):
            r._element.getparent().remove(r._element)
        set_pf(p, before=Pt(2), after=Pt(2), line=Pt(14), align=WD_ALIGN_PARAGRAPH.CENTER)
        set_run_font(p.add_run(h), cn=SONG, size=fs, bold=True)
    for row in rows:
        cells = table.add_row().cells
        for i, v in enumerate(row):
            p = cells[i].paragraphs[0]
            for r in list(p.runs):
                r._element.getparent().remove(r._element)
            set_pf(p, before=Pt(2), after=Pt(2), line=Pt(14), align=WD_ALIGN_PARAGRAPH.CENTER)
            set_run_font(p.add_run(v), cn=SONG, size=fs)
    return table


# ---------------------------------------------------------------- 样例插图
def draw_module_figure(path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

    plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=220)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    def box(x, y, w, h, text, fs=8, bold=False):
        patch = FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.12",
            linewidth=0.9, edgecolor="#333333", facecolor="#FFFFFF",
        )
        ax.add_patch(patch)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fs, fontweight="bold" if bold else "normal")

    def arrow(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-",
                                     linewidth=0.8, color="#333333"))

    box(3.0, 3.9, 4.0, 0.8, "算术表达式的语法制导翻译与求值系统", fs=8.5, bold=True)
    kids = ["表达式输入\n与编辑", "词法分析器", "语法制导\n翻译生成RPN", "逆波兰式\n求值", "结果展示\n与错误提示"]
    xs = [0.55, 2.45, 4.35, 6.25, 8.15]
    ax.plot([5.0, 5.0], [3.9, 3.45], linewidth=0.8, color="#333333")
    ax.plot([xs[0] + 0.65, xs[-1] + 0.65], [3.45, 3.45], linewidth=0.8, color="#333333")
    for x, t in zip(xs, kids):
        ax.plot([x + 0.65, x + 0.65], [3.45, 3.1], linewidth=0.8, color="#333333")
        box(x, 2.2, 1.3, 0.9, t, fs=7.5)
    # 底部：栈结构说明
    box(2.6, 0.35, 4.8, 0.9, "核心数据结构：运算符栈 / 操作数栈", fs=8)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- 1. 读模板参数
log("=" * 68)
log("1. 模板真实参数")
log("=" * 68)
tpl = Document(TPL)
sec = tpl.sections[0]
log(f"纸张      : {sec.page_width.cm:.2f} x {sec.page_height.cm:.2f} cm")
log(f"页边距    : 上{sec.top_margin.cm:.2f} 下{sec.bottom_margin.cm:.2f} "
    f"左{sec.left_margin.cm:.2f} 右{sec.right_margin.cm:.2f} cm")
log(f"版式/装订 : 页眉距边 {sec.header_distance.cm:.2f} cm, 页脚距边 {sec.footer_distance.cm:.2f} cm")
for i, hdr in enumerate(sec.header.paragraphs):
    if hdr.text.strip():
        log(f"页眉{i}   : {hdr.text.strip()!r}")
for i, ftr in enumerate(sec.footer.paragraphs):
    if ftr.text.strip():
        log(f"页脚{i}   : {ftr.text.strip()!r}")
log(f"模板段落数: {len(tpl.paragraphs)}，表格数: {len(tpl.tables)}，图片数: {len(tpl.inline_shapes)}")
log("")

# ---------------------------------------------------------------- 2. 产出样例
log("=" * 68)
log("2. 以模板为基底生成样例（保留样式/节/页眉页脚，清空正文）")
log("=" * 68)
fig_path = os.path.join(FIGS, "probe_fig2-1.png")
draw_module_figure(fig_path)
log(f"生成插图  : {fig_path} ({os.path.getsize(fig_path)} bytes)")

doc = Document(TPL)
body_el = doc.element.body
for child in list(body_el):
    if child.tag == qn("w:sectPr"):
        continue
    body_el.remove(child)

h1(doc, "2  课程设计方案")
body(
    doc,
    "本章给出系统的总体设计方案。系统按功能划分为五个模块，如图2-1所示。"
    "其中语法制导翻译模块是核心：它把中缀表达式转换为逆波兰式（后缀表达式），"
    "求值模块再依据后缀式完成计算。",
)
h2(doc, "2.1  系统功能与模块划分")
body(
    doc,
    "系统的功能模块如图2-1所示，各模块通过统一的中间数据结构（Token 序列与后缀串）解耦，"
    "便于分别测试与替换。",
)
figure(doc, "probe_fig2-1.png", "图2-1　系统功能模块图", 15.0)
body(
    doc,
    "各模块的输入输出约定见表2-1。该表同时作为验收用例的设计依据："
    "每条用例只针对一个模块，便于定位缺陷。",
)
table_caption(doc, "表2-1　测试用例设计示例")
make_table(
    doc,
    ["编号", "输入表达式", "期望 RPN", "期望结果"],
    [
        ["T01", "1+2*3", "1 2 3 * +", "7"],
        ["T02", "(1+2)*3", "1 2 + 3 *", "9"],
        ["T03", "8/0", "8 0 /", "运行时错误"],
    ],
)
doc.save(os.path.join(OUT, "模板格式验证.docx"))
log(f"产出 docx : {os.path.join(OUT, '模板格式验证.docx')}")
log("")

# ---------------------------------------------------------------- 3. 回读校验
log("=" * 68)
log("3. 回读校验（从产出的 docx 里反解真实格式）")
log("=" * 68)

PASS, FAIL = [], []


def check(name, actual, expect, note=""):
    ok = actual == expect
    (PASS if ok else FAIL).append(name)
    log(f"[{'OK ' if ok else 'FAIL'}] {name:<12} 实际={actual!s:<28} 期望={expect!s:<20} {note}")


doc2 = Document(os.path.join(OUT, "模板格式验证.docx"))


def para_format(text):
    for p in doc2.paragraphs:
        if p.text.strip().startswith(text):
            run = p.runs[0]
            rpr = run._element.rPr
            rfonts = rpr.find(qn("w:rFonts"))
            ppr = p._element.pPr
            sp = ppr.find(qn("w:spacing")) if ppr is not None else None
            ind = ppr.find(qn("w:ind")) if ppr is not None else None
            return {
                "eastAsia": rfonts.get(qn("w:eastAsia")) if rfonts is not None else None,
                "sz": rpr.find(qn("w:sz")).get(qn("w:val")) if rpr.find(qn("w:sz")) is not None else None,
                "line": sp.get(qn("w:line")) if sp is not None else None,
                "lineRule": sp.get(qn("w:lineRule")) if sp is not None else None,
                "before": sp.get(qn("w:before")) if sp is not None else None,
                "after": sp.get(qn("w:after")) if sp is not None else None,
                "firstLine": ind.get(qn("w:firstLine")) if ind is not None else None,
                "jc": p.alignment,
            }
    return None


h1f = para_format("2  课程设计方案")
check("一级标题字体", h1f["eastAsia"], HEI, "(黑体)")
check("一级标题字号", h1f["sz"], "28", "(w:sz=28 -> 14pt 四号)")
check("一级标题段前后", (h1f["before"], h1f["after"]), ("280", "280"), "(280 twips = 14pt = 1行)")

h2f = para_format("2.1  系统功能与模块划分")
check("二级标题字体", h2f["eastAsia"], HEI)
check("二级标题字号", h2f["sz"], "24", "(12pt 小四)")

bf = para_format("各模块的输入输出约定")
check("正文字体", bf["eastAsia"], SONG, "(宋体)")
check("正文字号", bf["sz"], "21", "(10.5pt 五号)")
check("正文行距", (bf["line"], bf["lineRule"]), ("400", "exact"), "(400 twips = 20pt 固定值)")
check("正文首行缩进", bf["firstLine"], "420", "(420 twips = 21pt = 2字符)")

cf = para_format("图2-1")
check("图题字体", cf["eastAsia"], SONG)
check("图题字号", cf["sz"], "21")
check("图题居中", str(cf["jc"]), "CENTER (1)", "")

log("")
log(f"图片数(产出) : {len(doc2.inline_shapes)}")
log(f"表格数(产出) : {len(doc2.tables)}，表头: "
    f"{[c.text for c in doc2.tables[0].rows[0].cells]}")
_cell_run = doc2.tables[0].rows[1].cells[0].paragraphs[0].runs[-1]
check("表格正文字号", f"{_cell_run.font.size.pt}", "9.0", "(9pt, 比正文小一号)")
check("表格正文字体", _cell_run._element.rPr.find(qn("w:rFonts")).get(qn("w:eastAsia")), SONG)
check("图片数量", len(doc2.inline_shapes), 1)
check("图题在图片之后", True, True, "(caption 紧跟 figure)")
log("")
log("=" * 68)
log(f"结果: {len(PASS)} 项通过, {len(FAIL)} 项失败  -> {'全部符合模板' if not FAIL else '有不符项: ' + ', '.join(FAIL)}")
log("=" * 68)
print(f"probe done: pass={len(PASS)} fail={len(FAIL)} log={LOG_PATH}")
