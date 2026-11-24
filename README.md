# 编译原理课程设计二 · 算术表达式的语法制导翻译与求值系统

> 一个**不带任何第三方依赖**的小型编译器前端：中缀表达式 → 词法分析 → 递归下降 + 综合属性（语法制导翻译）→ 逆波兰式 → 栈求值 → 浏览器界面展示。
> 交付物：可运行程序 + 课程设计报告（Word/PDF）+ 源码压缩包。

## 一句话架构

```
浏览器界面 (HTML/CSS/JS)  ──HTTP/JSON──▶  WebApi (JDK 内置 HttpServer)
                                                  │
Swing 备用壳 (SwingShell) ────────────────────────┴──▶ RpnService（纯计算，无界面依赖）
                                                          ├─ Lexer   → List<Token>
                                                          ├─ Parser  → 后缀串（综合属性）
                                                          └─ Evaluator → double
```

**核心约束**：`Lexer` / `Parser` / `Evaluator` / `RpnService` **不得 import 任何界面或网络 API**。这条约束是"界面可替换 + 核心可批量测试"的全部前提。

## 目录

| 路径 | 用途 |
| --- | --- |
| `src/rpn/` | Java 源码（单包，编译逻辑与界面分离） |
| `web/` | 前端单页：`index.html` / `style.css` / `app.js`，零 npm 依赖 |
| `report/` | 报告源文件：`草稿-报告二.md`（改这里，不直接改 docx） |
| `docs/` | 路线图、每日任务卡、架构决策记录 |
| `tools/` | `md2docx.py`（md→docx 模板渲染）、`make_figures_r2.py`（插图生成）、校验脚本 |
| `figs/` | 报告插图（脚本生成，勿手改） |
| `out/` | 生成物：docx、pdf、校验日志、预览图（不入库） |

## 构建与运行

```bat
:: 编译
"%JAVA_HOME%\bin\javac" -encoding UTF-8 -d out\classes src\rpn\*.java

:: 跑测试（不需要界面）
"%JAVA_HOME%\bin\java" -cp out\classes rpn.TestRunner

:: 启动程序（编译 + 起服务 + 自动开浏览器）
run.bat
```

环境：**JDK 25 LTS**（`JAVA_HOME` 已配置）、VS Code + Extension Pack for Java、Git。
不使用 Maven / Gradle：项目零第三方依赖，`javac` 直接编译最可靠，验收现场双击 `run.bat` 即可。

## 远程仓库

本地 `main` 跟踪 GitHub **私有**仓库：<https://github.com/zh483/rpn-translator>（候选题名之外不要再公开，避免抄袭风险）。

```bat
git push          :: 推送到远程
git pull          :: 拉取（单人开发一般用不到）
```

> **代理坑**：本机 git 原来全局配了 `http.proxy = http://127.0.0.1:7897`，代理软件没开时连 GitHub 会报
> `Failed to connect to github.com port 443 via 127.0.0.1`。已清除该全局配置（直连可用）。
> 若以后要用代理：`git config --global http.proxy http://127.0.0.1:7897`；
> 要恢复直连：`git config --global --unset http.proxy`。

## 报告流水线

1. 只改 `report/草稿-报告二.md`（Markdown 约定见 `report/报告写作约定.md`）。
2. 跑 `py -3.13 tools/md2docx.py`，产出 `out/报告二-草稿.docx` + 自动校验（字体字号、图表编号连号、正文引用检查）。
3. 用 Word 打开 → 另存为 PDF → 打印装订。

## 约定

- 中文注释；类名 PascalCase、方法 camelCase、常量 UPPER_SNAKE。
- 使用 `record` 表示不可变数据（Token、结果），`enum` 表示记号类型与错误类别。
- 提交信息：`feat: 词法分析器支持浮点常量`、`fix: 一元负号与减号歧义`。
- 错误一律通过 `CompileException`（类别 + 位置 + 期望集）抛出，禁止吞异常。
