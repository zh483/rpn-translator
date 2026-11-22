# Day 01 任务卡 · 2026-11-23（周一）

**时间盒：60–90 分钟** ｜ 目标：把 JDK 跑通、建立 C++→Java 心智映射、完成 `Token`/`TokenType`/`Lexer` 骨架。

## 0. 开工前 2 分钟自检

```bat
java -version
javac -version
```

两行都必须是 **25.0.5.1**。若不是：新开一个终端窗口再试（PATH 已改，旧窗口不会刷新）。

## 1. 交付物（4 个文件）

| 文件 | 要求 |
| --- | --- |
| `src/rpn/TokenType.java` | `enum TokenType { NUM, PLUS, MINUS, STAR, SLASH, PERCENT, LPAREN, RPAREN, EOF }` |
| `src/rpn/Token.java` | `public record Token(TokenType type, String text, int pos, double value)`，加 Javadoc 说明 `text` 保留原文、`pos` 为 0 基下标 |
| `src/rpn/CompileException.java` | 继承 `RuntimeException`，字段 `Kind kind`（`LEX`/`SYNTAX`/`RUNTIME`）+ `int pos`；消息格式 `[词法错误] 第 n 个字符：…` |
| `src/rpn/Lexer.java` | `public List<Token> scan(String src) throws CompileException`，**本轮只要求**：跳过空白、识别整数/小数、识别 8 个单字符运算符、非法字符抛错、末尾补 `EOF` |

## 2. 验收用例（全部通过才算 M1 的一半）

用临时 `main` 或直接在 `TestRunner` 里打表，逐条打印 `type/value/pos`：

| # | 输入 | 期望输出 |
| --- | --- | --- |
| 1 | `12` | `NUM(12.0) EOF` |
| 2 | `3.14` | `NUM(3.14) EOF` |
| 3 | `1+2` | `NUM(1) PLUS NUM(2) EOF` |
| 4 | `1 + 2` | 同上（空白被跳过） |
| 5 | `.5` | `NUM(0.5) EOF` |
| 6 | `5.` | `NUM(5.0) EOF` |
| 7 | `1$a` | 抛 `[词法错误] 第 2 个字符：非法字符 '$'` |

编译命令：

```bat
"%JAVA_HOME%\bin\javac" -encoding UTF-8 -d out\classes src\rpn\*.java
"%JAVA_HOME%\bin\java" -cp out\classes rpn.TestRunner
```

> 注意：源文件用 **UTF-8 无 BOM** 保存（VS Code 默认），`javac` 必须带 `-encoding UTF-8`，否则中文注释会报错。

## 3. 硬性约束（违反直接打回）

- [ ] 不得出现 `import java.awt` / `javax.swing` / `com.sun.net.httpserver`（核心层与界面无关）
- [ ] 不得出现魔法数字：token 位置、运算符判断统一走 `switch` 或 `TokenType` 映射
- [ ] `Lexer` 不修改输入串、不持有可变静态状态
- [ ] 每个 public 类/方法有 Javadoc；关键分支有中文行内注释解释**为什么**
- [ ] 异常消息必须含"第 n 个字符"

## 4. C++ → Java 对照卡（今天会用到）

| C++ | Java | 备注 |
| --- | --- | --- |
| `std::vector<char>` | `String` + `charAt` | Java 的 String 不可变，别想着原地改 |
| `std::string` 拼接 | `StringBuilder` | 循环里用 `+` 会创建大量临时对象（后面 Parser 必踩） |
| `const` 成员函数 | `final` / record | record 字段天然 final |
| 析构函数 / RAII | GC | 没有确定性析构，别指望 finally 当析构器 |
| `std::unique_ptr` | 直接引用 | Java 全靠引用，没有值语义对象 |
| `throw std::runtime_error` | `throw new RuntimeException` | 本项目用自定义 `CompileException` |
| `enum class` | `enum` | Java enum 是类，可带字段与方法 |
| `NULL`/`nullptr` | `null` | 但 record 里尽量别用 null，用 `Optional` 或空串 |
| `std::stod` | `Double.parseDouble` | 转换失败抛 `NumberFormatException`，本项目自己扫字符更可控 |
| `size_t i` | `int i` | 字符下标用 `int` 就够 |

## 5. 卡住怎么办

- **15 分钟无进展**：把报错原文 + 你试过的两种思路发我。
- **20 分钟规则**：我只给思路（例如"先写 7 条用例的期望输出表，再写扫描循环"），不给代码。
- **写完先自测再交**：贴出 7 条用例的真实输出。

## 6. 提交

```bat
git add -A
git commit -m "feat: 词法分析器 Token 定义与扫描骨架"
```

## 7. 明天预告（Day 02）

浮点边界（`.` 单独出现、`1.2.3`、超长数字）、位置信息贯穿、`TestRunner` 成型；然后进入属性文法手推题（3 道）。
