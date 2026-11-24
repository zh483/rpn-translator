# -*- coding: utf-8 -*-
"""make_figures_r2.py —— 生成报告二需要的插图（矢量风格 PNG，200dpi）。

产出：
  figs/fig2-1.png  系统功能模块图
  figs/fig2-2.png  语法制导翻译与求值流程图
  figs/fig3-1.png  图形界面设计线框图（正常态）
  figs/fig3-2.png  图形界面设计线框图（错误态）
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGS = os.path.join(ROOT, "figs")
os.makedirs(FIGS, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "SimSun"]
plt.rcParams["axes.unicode_minus"] = False

EDGE = "#333333"
FILL = "#FFFFFF"
ACCENT = "#DCE6F1"
WARN = "#FBE4E4"


def canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h), dpi=200)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100 * h / w)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, text, fs=8, bold=False, fill=FILL, lw=0.9, dashed=False):
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.4,rounding_size=0.8",
            linewidth=lw, edgecolor=EDGE, facecolor=fill,
            linestyle="--" if dashed else "-",
        )
    )
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, fontweight="bold" if bold else "normal", linespacing=1.4)


def arrow(ax, x1, y1, x2, y2, lw=0.8, head=True):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1), (x2, y2),
            arrowstyle="-|>" if head else "-",
            mutation_scale=8, linewidth=lw, color=EDGE, shrinkA=0, shrinkB=0,
        )
    )


# ---------------------------------------------------------------- 图2-1
def fig21():
    fig, ax = canvas(7.0, 4.0)
    box(ax, 18, 30.0, 64, 8.0, "算术表达式的语法制导翻译与求值系统", fs=9, bold=True, fill=ACCENT)

    xs = [3, 36, 69]
    labels = ["① 表达式输入与编辑\n（浏览器界面）", "② 词法分析器\n（Token 序列）",
              "③ 语法制导翻译\n（中缀 → 后缀）"]
    for x, t in zip(xs, labels):
        box(ax, x, 17.0, 28, 7.5, t, fs=7.5)
    labels2 = ["④ 逆波兰式求值\n（操作数栈）", "⑤ 结果展示\n（RPN + 结果）",
               "⑥ 错误检测与提示\n（词法/语法/运行）"]
    for x, t in zip(xs, labels2):
        box(ax, x, 4.0, 28, 7.5, t, fs=7.5)

    ax.plot([50, 50], [30, 25.5], color=EDGE, lw=0.8)
    ax.plot([17, 83], [25.5, 25.5], color=EDGE, lw=0.8)
    for x in [17, 50, 83]:
        ax.plot([x, x], [25.5, 24.5], color=EDGE, lw=0.8)
    for x in [17, 50, 83]:
        arrow(ax, x, 17.0, x, 11.5)
    fig.savefig(os.path.join(FIGS, "fig2-1.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- 图2-2
def fig22():
    fig, ax = canvas(7.0, 3.4)
    stages = ["中缀表达式\n1+2*3", "词法分析\nToken 序列", "递归下降\n+ 综合属性",
              "后缀串\n1 2 3 * +", "操作数栈\n求值", "结果\n7"]
    n = len(stages)
    w, gap = 12.5, 4.5
    total = n * w + (n - 1) * gap
    x = (100 - total) / 2
    y = 15.0
    for i, s in enumerate(stages):
        box(ax, x, y, w, 9.0, s, fs=7.5, fill=ACCENT if i in (2, 4) else FILL)
        if i:
            arrow(ax, x - gap, y + 4.5, x, y + 4.5)
        x += w + gap
    box(ax, 12, 2.0, 76, 7.0,
        "统一错误模型：[词法错误] / [语法错误] / [运行时错误] + 字符位置 + 期望集",
        fs=7.5, fill=WARN, dashed=True)
    arrow(ax, 50, 15.0, 50, 9.0)
    fig.savefig(os.path.join(FIGS, "fig2-2.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- 图3-1 / 3-2
def window(err=False):
    fig, ax = canvas(7.0, 3.6)
    # 浏览器外框
    ax.add_patch(Rectangle((2, 2), 96, 44, linewidth=1.0, edgecolor=EDGE, facecolor="#FFFFFF"))
    # 标签页条
    ax.add_patch(Rectangle((2, 41.0), 96, 5.0, linewidth=0.8, edgecolor=EDGE, facecolor="#E8E8E8"))
    ax.add_patch(Rectangle((3.5, 41.8), 34, 4.2, linewidth=0.8, edgecolor="#BBBBBB", facecolor="white"))
    ax.text(5, 43.9, "算术表达式翻译与求值系统", fontsize=6.5, va="center")
    ax.text(93, 43.9, "—  □  ×", fontsize=6.5, ha="right", va="center")
    # 地址栏
    ax.add_patch(Rectangle((4, 36.6), 92, 3.6, linewidth=0.7, edgecolor="#CCCCCC", facecolor="#F7F7F7"))
    ax.text(6, 38.4, "127.0.0.1:8080", fontsize=6.5, va="center", family="Consolas",
            color="#333333")

    ax.text(5, 32.5, "表达式：", fontsize=7.5, va="center")
    ax.add_patch(Rectangle((17, 29), 46, 6, linewidth=0.8, edgecolor="#888888", facecolor="white"))
    ax.text(18.5, 32, error_text if err else "1+2*3", fontsize=8.5, va="center",
            family="Consolas")
    ax.add_patch(Rectangle((66, 29), 14, 6, linewidth=0.8, edgecolor=EDGE, facecolor="#D9E2F3"))
    ax.text(73, 32, "翻译并求值", fontsize=7.5, ha="center", va="center")
    ax.add_patch(Rectangle((81, 29), 8, 6, linewidth=0.8, edgecolor=EDGE, facecolor="#EFEFEF"))
    ax.text(85, 32, "清空", fontsize=7.5, ha="center", va="center")

    panels = [("中缀表达式", "1+2*3"), ("逆波兰式", "1 2 3 * +"), ("计算结果", "7")]
    px = 5
    for i, (title, val) in enumerate(panels):
        ax.add_patch(Rectangle((px, 15), 28, 10, linewidth=0.7, edgecolor="#AAAAAA", facecolor="white"))
        ax.text(px + 1.5, 22.5, title, fontsize=7, color="#555555")
        ax.text(px + 1.5, 18.5, val, fontsize=10, family="Consolas")
        px += 30.5

    ax.add_patch(Rectangle((5, 6), 84, 6, linewidth=0.7, edgecolor="#C00000" if err else "#AAAAAA",
                           facecolor="#FDECEC" if err else "white"))
    if err:
        ax.text(6, 9, "[语法错误] 第 5 个字符: 期望 ')' 或运算符，实际读到 '*'", fontsize=7,
                color="#C00000", va="center")
        ax.text(6, 3.6, "  1 + 2 * ) 3", fontsize=7.5, family="Consolas", va="center")
        ax.text(27, 3.6, "^", fontsize=8, family="Consolas", va="center", color="#C00000")
    else:
        ax.text(6, 9, "就绪：支持 + - * / % ( ) 与整数、浮点数；错误将在此处给出位置指示。",
                fontsize=7, color="#666666", va="center")
    return fig


error_text = "1+2*)3"


def fig31():
    fig = window(False)
    fig.savefig(os.path.join(FIGS, "fig3-1.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig32():
    fig = window(True)
    fig.savefig(os.path.join(FIGS, "fig3-2.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    fig21(); fig22(); fig31(); fig32()
    for f in ("fig2-1.png", "fig2-2.png", "fig3-1.png", "fig3-2.png"):
        p = os.path.join(FIGS, f)
        print(f"{f:12s} {os.path.getsize(p):7d} bytes")
