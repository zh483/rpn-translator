# -*- coding: utf-8 -*-
"""定位报告模板 docx。

模板文件本身含学校封面、页眉页脚，不适合进公开仓库（文件名带学号姓名），
因此默认从仓库根目录找第一个非临时 .docx，也允许用 REPORT_TPL 指定。
"""
import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_template():
    """返回模板 docx 的路径；找不到时抛 FileNotFoundError。"""
    env = os.environ.get("REPORT_TPL")
    if env:
        if os.path.exists(env):
            return env
        raise FileNotFoundError("REPORT_TPL 指向的文件不存在: " + env)

    cands = [
        p for p in sorted(glob.glob(os.path.join(ROOT, "*.docx")))
        if not os.path.basename(p).startswith("~$")
    ]
    if not cands:
        raise FileNotFoundError(
            "仓库根目录没有 .docx 模板。请把课程设计模板放回根目录，"
            "或设置环境变量 REPORT_TPL 指向模板。"
        )
    return cands[0]


TPL = find_template()
