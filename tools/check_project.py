# -*- coding: utf-8 -*-
"""check_project.py —— 项目硬约束的机器执行者（门禁）。

约束不是写在文档里靠自觉，而是靠这个脚本判。任何一条 FAIL，都不提交、不进入下一天。

检查项：
  [FAIL] 文件编码必须是 UTF-8 无 BOM
  [FAIL] 必须声明 package rpn;
  [FAIL] 文件名 = public 类型名（含大小写），且类型名为 PascalCase
  [FAIL] public 类型必须有 Javadoc
  [FAIL] 核心层禁止 import 界面 / 网络 / IO 相关包
  [FAIL] 禁止用 tab 缩进（4 空格）
  [WARN] 行宽 > 100 字符
  [WARN] 方法名首字母应小写（camelCase）
  [WARN] 核心类里不要直接 System.out（应返回结果或抛异常）
  [WARN] 不要用 import java.util.* 通配符
  [FAIL] 报告 MD 里不得残留红色【提示】段
  [FAIL] run.bat / check.bat 必须纯 ASCII（cmd 按 GBK 解析批处理）

用法: py -3.13 tools/check_project.py
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "rpn")
REPORT_MD = os.path.join(ROOT, "report", "草稿-报告二.md")

CORE = {
    "Token", "TokenType", "CompileException", "Lexer", "Parser",
    "Evaluator", "RpnService", "ResultFormatter",
}
BOUNDARY_PREFIX = ("Web", "Swing", "Main", "TestRunner", "Practice")

FORBIDDEN_IN_CORE = [
    "java.awt", "javax.swing", "javax.imageio", "java.net",
    "com.sun.net.httpserver", "java.nio.file", "java.io",
]

ok, warn, fail = [], [], []


def add(kind, msg):
    {"OK": ok, "WARN": warn, "FAIL": fail}[kind].append(msg)


def javadoc_before(text, decl_pos):
    """decl 前 400 字符内是否有 /** ... */ 注释块。"""
    window = text[max(0, decl_pos - 400):decl_pos]
    return "/**" in window and "*/" in window


def check_java(path):
    name = os.path.basename(path)
    stem = name[:-5]
    raw = open(path, "rb").read()

    if raw.startswith(b"\xef\xbb\xbf"):
        add("FAIL", f"{name}: 含 UTF-8 BOM，请另存为 UTF-8 无 BOM")
        raw = raw[3:]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        add("FAIL", f"{name}: 不是 UTF-8 编码")
        return

    # package
    if not re.search(r"^\s*package\s+rpn\s*;", text, re.M):
        add("FAIL", f"{name}: 缺少 'package rpn;'")

    # 文件名 = public 类型名
    decls = list(re.finditer(r"(?m)^\s*public\s+(?:final\s+|abstract\s+|sealed\s+)?"
                             r"(class|record|interface|enum)\s+(\w+)", text))
    if not decls:
        if re.search(r"(?m)^\s*(?:final\s+|abstract\s+)?(class|record|interface|enum)\s+(\w+)", text):
            add("WARN", f"{name}: 没有 public 类型（顶格类型不可见）")
    else:
        d = decls[0]
        if d.group(2) != stem:
            add("FAIL", f"{name}: public {d.group(1)} {d.group(2)} 与文件名不一致")
        if not javadoc_before(text, d.start()):
            add("FAIL", f"{name}: public {d.group(1)} {d.group(2)} 缺少 Javadoc")

    if not re.fullmatch(r"[A-Z][A-Za-z0-9]*", stem):
        add("FAIL", f"{name}: 类名应为 PascalCase")

    # import 约束
    imports = re.findall(r"(?m)^\s*import\s+([\w.*]+)\s*;", text)
    is_core = stem in CORE
    for imp in imports:
        if imp.endswith(".*"):
            add("WARN", f"{name}: 通配符 import {imp}，请写具体类")
        if is_core:
            for bad in FORBIDDEN_IN_CORE:
                if imp == bad or imp.startswith(bad + "."):
                    add("FAIL", f"{name}: 核心层禁止 import {imp}（架构约束：核心与界面/IO 解耦）")
    if is_core and re.search(r"System\.out\.(print|printf)", text):
        add("WARN", f"{name}: 核心类里直接 System.out，应返回结果或抛异常")

    # 缩进 / 行宽
    for i, line in enumerate(text.splitlines(), 1):
        if "\t" in line:
            add("FAIL", f"{name}:{i}: 使用 tab 缩进，请改 4 空格")
            break
    for i, line in enumerate(text.splitlines(), 1):
        if len(line) > 100:
            add("WARN", f"{name}:{i}: 行宽 {len(line)} > 100")

    # 方法命名 camelCase
    for m in re.finditer(r"(?m)^\s+(?:public|private|protected)\s+"
                         r"(?:static\s+|final\s+|abstract\s+|synchronized\s+)*"
                         r"[\w<>\[\],.? ]+?\s+(\w+)\s*\(", text):
        meth = m.group(1)
        if meth in (stem,) or not meth[:1].isalpha():
            continue
        if meth[0].isupper():
            add("WARN", f"{name}: 方法名 '{meth}' 应为 camelCase（首字母小写）")


def check_bat():
    for name in ("run.bat", "check.bat"):
        p = os.path.join(ROOT, name)
        if not os.path.exists(p):
            continue
        raw = open(p, "rb").read()
        bad = sum(1 for b in raw if b > 127)
        if bad:
            add("FAIL", f"{name}: 含 {bad} 个非 ASCII 字节（cmd 按 GBK 解析会崩）")


def check_report(final: bool):
    if not os.path.exists(REPORT_MD):
        return
    text = open(REPORT_MD, encoding="utf-8").read()
    left = [ln.strip() for ln in text.splitlines() if ln.strip().startswith("> 提示")]
    if left:
        kind = "FAIL" if final else "WARN"
        add(kind, f"报告 MD 残留 {len(left)} 处红色提示"
                  + ("（定稿模式：必须删）" if final else "（草稿阶段允许，定稿时加 --final 检查）"))


def main():
    final = "--final" in sys.argv
    files = sorted(f for f in os.listdir(SRC) if f.endswith(".java")) if os.path.isdir(SRC) else []
    print(f"检查 {len(files)} 个 Java 文件" + ("（定稿模式）" if final else "") + "\n" + "-" * 62)
    for f in files:
        check_java(os.path.join(SRC, f))
    check_bat()
    check_report(final)

    for kind, items in (("FAIL", fail), ("WARN", warn)):
        for m in items:
            print(f"[{kind}] {m}")
    if not fail and not warn:
        print("[OK] 全部约束通过")

    print("-" * 62)
    print(f"结果: {len(ok)} OK / {len(warn)} WARN / {len(fail)} FAIL")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
